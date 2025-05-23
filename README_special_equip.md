# Special Equipment

1. 所有代码修改好之后, build，得到 `build` 文件夹
```bash
npm run build 
```

2. 创建 `special_equipment` 文件夹
```bash
mkdir -p special_equipment
```

3. 将 `build` 文件夹复制到 `special_equipment` 文件夹下
```bash
cp -r build/ special_equipment/
```

4. 将 `backend` 文件夹复制到 `special_equipment` 文件夹下
```bash
cp CHANGELOG.md special_equipment/
cp -r backend/ special_equipment/
```

5. 将 `nginx_for_test_env` 文件夹复制到 `special_equipment` 文件夹下
```bash
cp -r nginx_for_test_env/ special_equipment/
```
修改 `docker-compose.yaml`
```yaml
    volumes:
      - /home/duyuhao/special_equipment/nginx_for_test_env/nginx.conf:/etc/nginx/nginx.conf:ro
```
修改 `nginx.conf`
```angular2html
proxy_pass http://192.168.94.187:18080;
```

6. 将 `special_equipment` 文件夹打包压缩为 `special_equipment.zip`
```bash
zip -r special_equipment.zip special_equipment
```

7. 将 `special_equipment.zip` 传输到L40服务器
```bash
scp -r -P 10022 -i ~/.ssh/id_rsa /data/yuhao/workspace/open-webui/special_equipment.zip duyuhao@58.241.42.210:/home/duyuhao/
```

8. 解压 `special_equipment.zip` 到 `/home/duyuhao/special_equipment`
```bash
unzip special_equipment.zip -d /home/duyuhao/special_equipment
```

9. 启动测试环境
```bash
cd /home/duyuhao/special_equipment/nginx_for_test_env
docker-compose up -d
```

10. 启动后端服务
```bash
cd /home/duyuhao/special_equipment/backend
bash start.sh
```

11. 打开浏览器访问 `http://58.241.42.210:10086`
    
    导入函数, 修改api地址为 192.168.94.187
    
    设置注册不需要管理员认证
    
    然后模型需要设置public
