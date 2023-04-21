import re
import sys
import html
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests as requests
import yaml


def apply_content(yaml_content, operator, op_data):
    op_type = operator.split("_")[0]
    name = operator.split("_")[1]
    yaml_obj = yaml_content[name]
    remove_dict = []
    for obj_item in yaml_obj:
        if re.match(op_data, obj_item["name"]) is not None:
            if op_type == "remove":
                remove_dict.append(obj_item)
    for proxy_group in yaml_content["proxy-groups"]:
        for delete in remove_dict:
            if delete['name'] in proxy_group['proxies']:
                proxy_group['proxies'].remove(delete['name'])
    for delete in remove_dict:
        yaml_obj.remove(delete)


def process_with_data(yaml_content, data):
    operations = data.split(";")
    for operation in operations:
        operator = operation.split(":")[0]
        op_data = operation.split(":")[1]
        apply_content(yaml_content, operator, op_data)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if re.match(f'.*?.*&.*', self.path) is None:
            return
        # 解析GET请求参数
        parm = self.path.split('?')[1].split('&')
        url = parm[0].split('=')[1]
        data = parm[1].split('=')[1]

        my_user_agent = {'User-agent': 'Mozilla/5.0'}
        # 下载网址内容
        response = requests.get(url, headers=my_user_agent)
        content = response.content.decode("utf-8")
        yaml_content = yaml.unsafe_load(html.unescape(content.replace("!", "")))

        process_with_data(yaml_content, data)
        response_content = yaml.safe_dump(yaml_content, allow_unicode=True).encode()
        # 构建响应并返回
        self.send_response(200)
        # 复制网址响应的头部信息到本地响应
        for key, value in response.headers.items():
            if key == "Content-Length":
                value = str(len(response_content))
            self.send_header(key, value)

        self.end_headers()
        self.wfile.write(response_content)
        # self.wfile.write(yaml.safe_dump(yaml_content).encode())


if __name__ == '__main__':
    # 解析命令行参数
    if len(sys.argv) < 2:
        print('Usage: python http_server.py [port]')
        sys.exit(1)
    port = int(sys.argv[1])

    # 启动HTTP服务器
    httpd = HTTPServer(('0.0.0.0', port), MyHTTPRequestHandler)
    print('HTTP server is running on port', port)
    httpd.serve_forever()
