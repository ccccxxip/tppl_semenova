NASM=nasm

average: main.o
	ld -z noseparate-code -o average main.o

main.o: main.asm
	$(NASM) -f elf64 main.asm -o main.o

run: average
	./average data.txt

clean:
	rm -f main.o average

.PHONY: run clean