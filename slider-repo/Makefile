SDRC=python -m sdrc.driver
all: hello

hello:
	$(SDRC) build examples/hello.sdr -o build/hello.ll
	lli build/hello.ll

acs:
	$(SDRC) build examples/demo_acs_v1.sdr -o build/demo_acs_v1.ll
	clang build/demo_acs_v1.ll runtime/acs_v1.c -lpthread -o build/demo_acs_v1
	./build/demo_acs_v1

clean:
	rm -rf build dist site .mypy_cache __pycache__
