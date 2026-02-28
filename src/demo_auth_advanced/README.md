```shell
# Generate an RSA private key, of size 2048 into file jwt-privat.pem
openssl genrsa -out jwt-private.pem 2048

# Extract the public key from the key pair, wich can be used in a certificate
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
# -in входной файл приватного ключа, -outform PEM формат выходного файла PEM — это текстовый формат, -pubout вычисли и выведи только публичную часть, -out jwt-public.pem имя выходного файла
```