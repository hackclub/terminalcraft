#/bin/bash

echo "Please select a compiler (gcc, g++)"
read tool
echo "Select the file you wish to compile"
read source
if [ ! -f "$source" ]; then
    echo "Error: Source file '$source' not found."
    exit 1
fi
echo "Select flags (-Wall, -Wextra)"
read flags
echo "Select output name (do not type .o)"
read output_name
echo "Compiling"
$tool $source $flags -o $output_name.o  
if "$tool" "$source" $flags -o "$output_name"; then
    echo "Compilation successful! Output file is '$output_name'."
    read -p "Run the program? (y/n) " -n 1 -r
    echo 

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running '$output_name'..."
        ./"$output_name"
    fi
else
    echo "Compilation failed."
    exit 1
fi

    
