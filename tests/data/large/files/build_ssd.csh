#!/bin/tcsh -f
#
# ./build_ssd.csh
#
# Build a BBC Micro SSD image of sample programs which can be run using the BBC Tube coprocessor
# versions of OPC7 (PiTubeDirect or the Matchbox/GOP FPGA versions)
#

rm -rf disk
mkdir -p disk
set ASM = opc7asm.py
set MMB = ../utils/mmb_utils/beeb
set SSD = OPC7DEMO.ssd
set testlist = ( pi-spigot-rev e-spigot-rev bigsieve sieve nqueens math32 )

pushd disk
foreach test ( $testlist )
    set newname = `echo $test | awk '{gsub("-.*-","");print substr($0,0,7)}'`
    echo "Building test $test as $newname"
    ## dummy assembly to get a binary size
    set size = `python3 ../${ASM}  -f ../tests/${test}.s  | grep ssembled| awk '{print $2+10}'`
    echo $size "words"
    
    python3 ../${ASM} -g bin --start_adr 0x1000 --size $size -f ../tests/${test}.s -o ${newname} > ../tests/${test}.lst
    echo $newname | awk '{printf("\$.%s\t1000\t1000",$1)}' > ${newname}.inf
end
popd
# Build the SSD image
rm -f ${SSD}
${MMB} blank_ssd ${SSD}
${MMB} putfile ${SSD} disk/*
${MMB} info ${SSD}

