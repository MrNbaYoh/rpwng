all: build/rop_loader.bin build/rop.bin

build/rop.bin: rop.py macros.py constants.py
	@python3 $(PYROP)/pyrop.py rop.py build/rop.bin

build/rop_loader.bin: rop_loader.py macros.py constants.py
	@python3 $(PYROP)/pyrop.py rop_loader.py build/rop_loader.bin

clean:
	@rm -rf build
