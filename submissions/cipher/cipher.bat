if exist .\dist\ {
    node .\dist\index.js
} else {
    echo "Build not found. Compiling..."
    npm i
    npm run build 
    node .\dist\index.js
}