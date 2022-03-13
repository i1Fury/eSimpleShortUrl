# eShortUrl

Dis ting is just a server and client that has a url shortener, image server, and text bin. The client is for windows and is rather epic.

You can test some of the features over at https://elliotcs.dev/

Use this to set up ssl and proxies:
 - https://nginxproxymanager.com/guide/

Example systemctl config:
`short.service`
```
[Unit]
Description=Simple url shortener server
After=network.target

[Service]
User=root
WorkingDirectory=/root/main/short
ExecStart=/root/main/dev/DevEnv/bin/uwsgi --socket 0.0.0.0:7001 --protocol=http -w wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

To set up through the Nginx Proxy Manager panel:
1. Create a wildcard SSL cert for your domain(instructions online, you need to complete a dns challenge!)
2. Add a proxy for your domain for `*.domain.com` and `domain.com` in the same proxy.
3. Point the proxy to the SSL we created in step 1. I like to enable Force SSL.
4. To allow for the subdomain routing to be handled by Flask instead of nginx, pass this in to the Nginx Proxy Manager advanced tab for the proxy host:
```
location / {
         proxy_pass $forward_scheme://$server:$port;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP  $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
