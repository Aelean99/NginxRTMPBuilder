import asyncio
import pathlib


libraries = (
    "https://github.com/nginx/nginx.git",
    "https://github.com/vision5/ngx_devel_kit",
    "https://github.com/arut/nginx-rtmp-module",
    "https://github.com/openresty/set-misc-nginx-module",
    "https://github.com/alibaba/nginx-http-concat",
    "https://github.com/vision5/ngx_auto_lib",
)

LIB_DEPENDENCIES = "apt install libpcre3 libpcre3-dev libssl-dev zlib1g-dev"

CONFIGURE_OPTIONS = "--with-http_ssl_module " \
                    "--with-http_secure_link_module " \
                    "--add-module=../ngx_devel_kit " \
                    "--add-module=../nginx-rtmp-module " \
                    "--add-module=../set-misc-nginx-module " \
                    "--add-module=../nginx-http-concat " \
                    "--add-module=../ngx_auto_lib"

root_dir = pathlib.Path().cwd()
NGINX_BUILD_DIR = root_dir.joinpath("nginx-build")
NGINX_OBJS_DIR = f"{NGINX_BUILD_DIR}/nginx/objs"
NGINX_CONF_DIR = f"{NGINX_BUILD_DIR}/nginx/conf"
NGINX_LOCAL_DIR = "/usr/local/nginx"
NGINX_SBIN_DIR = f"{NGINX_LOCAL_DIR}/sbin"
NGINX_LOGS_DIR = f"{NGINX_LOCAL_DIR}/logs"


class NginxBuilder:
    def __init__(self):
        self.create_dirs()

    def create_dirs(self):
        dirs = (NGINX_BUILD_DIR, NGINX_SBIN_DIR, NGINX_LOGS_DIR)
        [pathlib.Path(path).mkdir(exist_ok=True, parents=True) for path in dirs]

    async def run(self, query):
        coro = await asyncio.create_subprocess_shell(query,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        (stdout, stderr) = await coro.communicate()
        if stdout:
            print("stdout:", stdout.decode())
        if stderr:
            print("stderr:", stderr.decode())

    async def fetch_modules(self):
        tasks = [self.run(f"cd {NGINX_BUILD_DIR} && git clone {uri}") for uri in libraries]
        tasks.append(self.run(LIB_DEPENDENCIES))
        await asyncio.gather(*tasks)

    async def build_nginx(self):
        await self.run(f"cd {NGINX_BUILD_DIR}/nginx && ./auto/configure {CONFIGURE_OPTIONS} && make -j 4")
        await self.run(f"cp {NGINX_OBJS_DIR}/nginx {NGINX_SBIN_DIR}")
        await self.run(f"cp -r {NGINX_CONF_DIR} {NGINX_LOCAL_DIR}")
        await self.run(f"touch {NGINX_LOGS_DIR}/error.log")
        await self.run(f"{NGINX_SBIN_DIR}/nginx -t")

    async def build_all(self):
        await self.fetch_modules()
        await self.build_nginx()


if __name__ == '__main__':
    builder = NginxBuilder()
    asyncio.run(builder.build_all())
