import { createProxyMiddleware } from 'http-proxy-middleware';

export const maxDuration = 60

export default function (req, res) {
    let target = ''
    // 代理目标地址
    // 这里使用 backend 主要用于区分 vercel serverless 的 api 路径
    // target 替换为你跨域请求的服务器 如： http://hl.hamflx.cn:8000
    if (req.url.startsWith('/api')) {
        target = 'http://hl.hamflx.cn:8000'
    }
    // 创建代理对象并转发请求
    createProxyMiddleware({
        target,
        changeOrigin: true,
        pathRewrite: {
            // 通过路径重写，去除请求路径中的 `/api`
            // 如果开启了,那么 /api/user/login 将被转发到 http://hl.hamflx.cn:8000/user/login
            //'^/api/': '/',
        },
    })(req, res)
}
