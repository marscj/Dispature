1. 生成 Oauth2 key 方法

import base64
base = base64.b64encode('client_id:client_secret'.encode('utf-8'))

grant_type password
username username
password password
Authorization Basic base

Authorization: Bearer access_token
