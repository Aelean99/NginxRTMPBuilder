import pathlib
import subprocess

libraries = (
    "https://github.com/nginx/nginx.git",
    "https://github.com/vision5/ngx_devel_kit",
    "https://github.com/arut/nginx-rtmp-module",
    "https://github.com/openresty/set-misc-nginx-module",
    "https://github.com/alibaba/nginx-http-concat",
    "https://github.com/vision5/ngx_auto_lib",
)

root_dir = pathlib.Path().cwd()

LIB_DEPENDENCIES = "apt install libpcre3 libpcre3-dev libssl-dev zlib1g-dev"


def run(query):
    with subprocess.Popen([query], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        if proc.stdout:
            print("stdout:", proc.stdout.read().decode())
        if proc.stderr:
            print("stderr:", proc.stderr.read().decode())


CONFIGURE_OPTIONS = "--with-http_ssl_module " \
                    "--with-http_secure_link_module " \
                    "--add-module=../ngx_devel_kit " \
                    "--add-module=../nginx-rtmp-module " \
                    "--add-module=../set-misc-nginx-module " \
                    "--add-module=../nginx-http-concat " \
                    "--add-module=../ngx_auto_lib"


def main():
    [run("cd {0} && git clone {1}".format(root_dir, uri)) for uri in libraries]
    run(LIB_DEPENDENCIES)

    nginx_dir = root_dir.joinpath("nginx")
    run("cd {0} && ./auto/configure {1} && make -j 4".format(nginx_dir, CONFIGURE_OPTIONS))

    new_nginx_dir = pathlib.Path("/usr/local/nginx/sbin/")
    new_nginx_dir.mkdir(exist_ok=True, parents=True)

    logs_dir = pathlib.Path("/usr/local/nginx/logs")
    logs_dir.mkdir(exist_ok=True, parents=True)

    run(f"cd {logs_dir} && touch error.log")
    run(f"cp {nginx_dir}/objs/nginx {new_nginx_dir}")
    run(f"cp -r {nginx_dir}/conf {new_nginx_dir.parent}")

    run(f"{new_nginx_dir}/nginx -t")


if __name__ == '__main__':
    main()
