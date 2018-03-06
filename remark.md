1. 生成 Oauth2 key 方法

import base64
print(str(base64.b64encode('client_id:client_secret'.encode('utf-8'))))
