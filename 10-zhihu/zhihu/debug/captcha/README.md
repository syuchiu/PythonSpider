## 知乎模拟登陆教程（2019-03）

参考了两篇文章：

- https://mp.weixin.qq.com/s/XplpQ6QUophvgfyMszk0Hg
- https://mp.weixin.qq.com/s/Hd0t4Qp50Z1nBN6bAk-YUQ

模拟登陆知乎有两个难点：验证码和加密。

第一篇文章破解加密的过程很详细，把踩坑的过程都写进去了，我自己一步一步做得时候也确实遇到了那些问题；第二篇文章里有较完整的代码，代码风格整洁简练，有完善的破解验证码的方法，但是缺少最后一道加密的步骤。

我结合了两篇文章，花了两天时间把整个过程实现了一遍，在第二篇文章的代码基础上做了补充。



大部分坑都在前面的两篇文中提到了，总结几个我踩的坑：

1. 请求验证码的过程中一定要用最原始的headers，不要多加字段；
2. 请求登陆页面是需要额外的三个字段：content-type, x-xsrftoken, x-zse-83，其中x-xsrftoken是通过获取set-cookie的值得到的；
3. signature字段是由grant_type, client_id, source, timestamp四个参数加密而成的，其中除了timestamp外都是固定的；
4. form data构造完之后，要先按照顺序encode，再传入加密函数，才能正确得到加密后的字符串（文一中就是缺少这一步）。
5. execjs依赖于node环境，最好和我使用的node版本一致：v11.10.0

如果有问题的可以联系我：897139816@qq.com

