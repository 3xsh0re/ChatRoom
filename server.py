import socket
import SSL
from need_module import json, logging, time


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建socket对象
    s_addr = ("0.0.0.0", 9999)
    s.bind(s_addr)  # 绑定地址和端口

    logging.info("UDP Server on %s:%s...", s_addr[0], s_addr[1])

    user = {}  # 存放字典{name:addr}

    print("----------服务器已启动-----------")
    print("Bind UDP on " + str(s_addr))
    print("等待客户端数据...")
    server = SSL.Server()

    while True:
        try:
            data, addr = s.recvfrom(1024)  # 等待接收客户端消息存放在2个变量data和addr里
            json_data = json.loads(data.decode("utf-8"))

            if "client_hello" in json_data:  # 接收SSL握手请求
                json_data = json.loads(data.decode("utf-8"))
                client_name = json_data["client_hello"]
                server_hello = server.respond_to_client_hello(client_name)

                # 向客户端发送握手消息
                hello = {"server_hello": server_hello}
                hello_json = json.dumps(hello, ensure_ascii=False)
                s.sendto(hello_json.encode("utf-8"), addr)

                # 向客户端发送证书
                with open(f"./Server_req.crt", "r") as file:
                    crt_data = str(file.read())
                    s.sendto(crt_data.encode("utf-8"), addr)
                    print("\033[32m[+]\033[0m服务端证书发送完成!")

                # 接收客户端证书
                while True:
                    data, addr = s.recvfrom(4096)
                    crt_data = data.decode("utf-8")
                    if len(crt_data) != 0:
                        break
                if "NOT_PASS_VERIFY" in crt_data:
                    print(f"\033[31m[-]\033[0m没有通过客户端验证,本次连接请求结束")
                else:
                    with open(f"{client_name}_req.crt", "w") as csr_file:
                        csr_file.write(crt_data)
                    print(f"\033[32m[+]\033[0m客户端证书接收成功")
                    # 验证证书
                    if server.verify_client_certificate(client_name):
                        # 接收密钥
                        print(f"\033[32m[+]\033[0m正在等待客户端传输密钥")
                        while True:
                            data, addr = s.recvfrom(1024)  # 等待接收客户端消息存放在2个变量data和addr里
                            json_data = json.loads(data.decode("utf-8"))
                            if len(json_data) != 0:
                                break
                        # 下面为本次客户端的共享密钥
                        shared_secret_enc = json_data["shared_secret"]
                        # RSA解出密钥,等待实现


            # 下面都是普通消息处理分支

            elif json_data["message_type"] == "init_message":
                if json_data["content"] not in user:  # address不等于addr时执行下面的代码
                    user[json_data["content"]] = addr
                    user_list = [i for i in user.keys()]
                    json_data["online_user"] = f"{user_list}"
                    json_str = json.dumps(json_data, ensure_ascii=False)
                    for address in user.values():
                        s.sendto(
                            json_str.encode("utf-8"), address
                        )  # 发送data和address到客户端
                    print(json_data["content"] + "进入了聊天室")
                    print(f"当前在线用户{user_list}")

            elif json_data["message_type"] == "leave_message":
                if json_data["content"] in user:  # address不等于addr时执行下面的代码
                    user.pop(json_data["content"])
                    user_list = [i for i in user.keys()]
                    for address in user.values():
                        s.sendto(data, address)  # 发送data和address到客户端
                    print(json_data["content"] + "离开了聊天室")
                    print(f"当前在线用户{user_list}")
                    continue

            elif json_data["chat_type"] == "normal":
                if json_data["message_type"] != "file":
                    for address in user.values():
                        if address != addr:
                            s.sendto(data, address)  # 发送data和address到客户端

            elif json_data["chat_type"] == "private":
                recv_user = json_data["recv_user"]
                send_user = json_data["send_user"]
                if json_data["message_type"] != "file-data":
                    s.sendto(data, user[recv_user])  # 发送data和address到客户端

                else:
                    filename = json_data["file_name"]
                    data_size = int(json_data["file_length"])
                    print("文件大小为" + str(data_size))
                    recvd_size = 0
                    data_total = b""
                    j = 0
                    while not recvd_size == data_size:
                        j = j + 1
                        if data_size - recvd_size > 1024:
                            data, addr = s.recvfrom(1024)
                            recvd_size += len(data)
                            print("第" + str(j) + "次收到文件数据")
                        else:  # 最后一片
                            data, addr = s.recvfrom(1024)
                            recvd_size = data_size
                            print("第" + str(j) + "次收到文件数据")
                        data_total += data

                    fhead = len(data_total)
                    message = {}
                    message["chat_type"] = "private"
                    message["message_type"] = "file-data"
                    message["file_length"] = str(fhead)
                    message["file_name"] = json_data["file_name"]
                    message["send_user"] = json_data["send_user"]
                    message["recv_user"] = json_data["recv_user"]
                    message["content"] = ""
                    jsondata = json.dumps(message, ensure_ascii=False)
                    s.sendto(jsondata.encode("utf-8"), user[recv_user])

                    print("开始发送文件数据...")
                    for i in range(len(data_total) // 1024 + 1):
                        time.sleep(0.0000000001)  # 防止数据发送太快，服务器来不及接收出错
                        if 1024 * (i + 1) > len(data_total):  # 是否到最后
                            s.sendto(
                                data_total[1024 * i :], user[recv_user]
                            )  # 最后一次剩下的数据传给对方
                            print("第" + str(i + 1) + "次发送文件数据")
                        else:
                            s.sendto(
                                data_total[1024 * i : 1024 * (i + 1)], user[recv_user]
                            )
                            print("第" + str(i + 1) + "次发送文件数据")

                    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(
                        '%s: "%s" 文件发送完成! from %s:%s [目标:%s] at %s'
                        % (
                            send_user,
                            filename,
                            addr[0],
                            addr[1],
                            user[recv_user],
                            now_time,
                        )
                    )

        except ConnectionResetError:
            logging.warning("Someone left unexpectedly.")


if __name__ == "__main__":
    main()
