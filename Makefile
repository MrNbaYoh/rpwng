export PYROP:="$(CURDIR)/pyrop"

all: ropdb/DB.py code/build game/build

ropdb/DB.py:
	@cp ropdb/$(REGION).py ropdb/DB.py

code/build:
	@cd code && make

game/build: rop/build
	@cd game && make

rop/build:
	@cd rop && make

clean:
	@rm ropdb/DB.py
	@cd game && make clean
	@cd rop && make clean
	@cd code && make clean
