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
workdir = root_dir.joinpath("ngx")
pathlib.Path(workdir).mkdir(exist_ok=True, parents=True)
print(workdir)


async def run(query):
    coro = await asyncio.create_subprocess_shell(query,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    (stdout, stderr) = await coro.communicate()
    if stdout:
        print("stdout:", stdout.decode())
    if stderr:
        print("stderr:", stderr.decode())


async def apt_install():
    await run(f"apt install libpcre3 libpcre3-dev libssl-dev zlib1g-dev")


async def git_clone(uri):
    await run(f"cd {workdir} && git clone {uri}")


async def main():
    tasks = [git_clone(uri) for uri in libraries]
    tasks.append(apt_install())
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
