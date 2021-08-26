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

root_dir = pathlib.Path().cwd()
ngx_dir = root_dir.joinpath("ngx")
pathlib.Path(ngx_dir).mkdir(exist_ok=True, parents=True)

LIB_DEPENDENCIES = "apt install libpcre3 libpcre3-dev libssl-dev zlib1g-dev"


async def run(query):
    coro = await asyncio.create_subprocess_shell(query,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    (stdout, stderr) = await coro.communicate()
    if stdout:
        print("stdout:", stdout.decode())
    if stderr:
        print("stderr:", stderr.decode())


CONFIGURE_OPTIONS = "--with-http_ssl_module " \
                    "--with-http_secure_link_module " \
                    "--add-module=../ngx_devel_kit " \
                    "--add-module=../nginx-rtmp-module " \
                    "--add-module=../set-misc-nginx-module " \
                    "--add-module=../nginx-http-concat " \
                    "--add-module=../ngx_auto_lib"


async def main():
    tasks = [run(f"cd {ngx_dir} && git clone {uri}") for uri in libraries]
    tasks.append(run(LIB_DEPENDENCIES))

    await asyncio.gather(*tasks)

    nginx_dir = ngx_dir.joinpath("nginx")
    await run(f"cd {nginx_dir} && ./auto/configure {CONFIGURE_OPTIONS} && make -j 4")


if __name__ == '__main__':
    asyncio.run(main())
