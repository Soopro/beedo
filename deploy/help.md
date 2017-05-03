# 部署在 CentOS 7

## 服务端环境配置

### 操作系统

CentOS 7

### 安装服务

1. 更新源:
  `sudo yum update`
  `sudo yum install epel-release`

2. 安装 webserver nginx:
  `sudo yum install nginx`
  `sudo systemctl enable nginx`

3. 安装 扩展支持:
  `sudo yum install gcc libffi-devel python-devel openssl-devel`
  有的 python 库需要这些支持，比如 pycrypto

4. 安装 python 包管理工具 pip:
  `curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"`
  `sudo python get-pip.py`
  or
  go http://dl.fedoraproject.org/pub/epel/ find latest one
  and `rpm -iUvh` with it.

5. 安装 wsgi容器 gunicorn:
    `pip install gunicorn`

6. 安装 进程管理、守护 supervisor:
    `sudo yum install supervisor`
    `sudo chkconfig supervisord on`

7. 安装git
    `sudo yum install git`


### 配置服务

#### 配置防火墙:

使用ucloud的话不推荐在服务器内配置防火墙。如果非要配置的话使用 `firewall-cmd` 详见:
```
https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-using-firewalld-on-centos-7
```


#### 配置 nginx:

1. 进入配置目录，`cd /etc/nginx/conf.d/`

2. 编辑配置文件 beedo （beedo 是配置名称，可以根据需要改）
    `vi beedo`

3. 输入配置(以下是范例，要根据实际的情况修改):
    <pre>
      server {
          listen 80;
          server_name  yourdomain.com;
          client_max_body_size 1M;

          location / {
              proxy_pass http://127.0.0.1:6002;
              proxy_set_header Host                $http_host;
              proxy_set_header X-Real-IP           $remote_addr;
              proxy_set_header X-Forwarded-For     $proxy_add_x_forwarded_for;
          }
      }
    </pre>

5. 别忘记把nginx的log_format也改改：
  (gunicorn 里面也记录了，但是gunicorn 里面 没有按照时间分割)
  ```
  log_format  main  '$remote_addr "$remote_user" [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  ```

6. 启动/停止/重启 nginx:
    启动: `service nginx start`

    停止: `service nginx stop`

    重启:
    `nginx -s reload` (这个失败会返回错误)
    or
    'service nginx restart'

    修改配置以后必须要重启一下nginx

#### 配置 gunicorn:

1. 在 beedo 项目目录中找到 ***deploy*** 目录
2. 根据项目需要写 gunicorn 的启动py文件(要留意配置的文件在是否真的存在)。
    例：
    <pre>
    <code>
      #coding=utf-8
      from __future__ import absolute_import
      import multiprocessing

      bind = "127.0.0.1:5000"
      workers = multiprocessing.cpu_count() * 2 + 1
      accesslog = "logs/api.access.log"
      errorlog = "logs/api.error.log"
      pidfile = "logs/api.pid"
    </code>
    </pre>

    说明：
      * ***bind*** 是端口号和ip地址，根据需要配置
      * ***workers*** 是进程数，这里是计算出来了一个"合理"的进程数
      * Log 的格式 需要做一些调整 避免反向代理后 ip 全是 127....的问题
    ```
    _log_str = '%(t)s %(u)s \'%(r)s\' %(s)s %(b)s \'%(f)s\''
    _log_ip = '<%({X-Real-IP}i)s> [%({X-Forwarded-for}i)s]'
    access_log_format = '{} {}'.format(_log_str, _log_ip)
    ```


#### 配置 supervisor:

1. 进入 /etc/supervisord.d/ 目录
    `cd /etc/supervisord.d/`
   注: 万一老是起不来的话，看看 /var/log/supervisor/supervisord.log 里面的。
2. 编辑配置文件 beedo.ini (centos 上的是用 ini)
    `vi beedo.ini`
3. 输入配置范例
    <pre>
      [program:beedo]
      user=root
      command=gunicorn -c deploy/prd_beedo.py beedo:app
      autostart=true
      autorestart=true
      directory=/var/www/beedo
      redirect_stderr=true
    </pre>

4. 启动/停止/重启 supervisor:

    启动: `service supervisord start`

    停止: `service supervisord stop`

    重启: `service supervisord restart`

5. supervisor控制命令:

    启动: `supervisorctl start <app>`

    关闭: `supervisorctl stop <app>`

    重启: `supervisorctl restart <app>`

    说明: `<app>` 可以是 all 或者具体的 app 名称。


#### 设置 ssh key:

1. 执行 `ssh-keygen`
2. `cd ~/.ssh`
3. `id_rsa.pub` 这是你的公钥，可以将它加到有权限的github账号中，方便部署


### 部署代码:

1. `mkdir /var/www` 创建 www 目录，
2. `cd /var/www`
3. 从github上拉源
    1. cleon beedo 项目

      `git clone git@github.com:Soopro/beedo.git`
      `cd beedo`
      `git pull origin master`



#### 部署Supmice:

3. `cd /var/www/beedo` 进入 beedo 目录
4. `pip install -r requirements.txt` 安装依赖包


### 启动服务
1. `nginx start` or `nginx -s reload`
2. `service supervisord start` or `service supervisord restart`
3. `supervisorctl start all` or `supervisorctl restart all`
