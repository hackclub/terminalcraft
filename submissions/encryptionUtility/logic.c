#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>

#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/evp.h>
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <openssl/err.h>

#include "logic.h"
#include "log.h"
#include "functions.h"

// Helper functions for common operations
char *getKeyContent(int keySource, const char *defaultFilename, const char *promptMsg)
{
    char *keyContent = NULL;
    size_t keyContentLength = 0;

    if (keySource == 1)
    { // From text
                char tempPrompt[256];
        sprintf(tempPrompt, "%s: ", promptMsg);
        keyContent = getString(tempPrompt);
        if (keyContent == NULL || strlen(keyContent) == 0)
            return NULL;
        printf("%s: %.20s...\n", promptMsg, keyContent);
    }
    else if (keySource == 0)
    { // From file
        char *filename;
        if (defaultFilename)
        {
            char tempString[256]; // Use a buffer with sufficient size
            sprintf(tempString, "Enter the %s filename [%s]: ", promptMsg, defaultFilename);
            filename = getString(tempString);

            if (filename == NULL)
                return NULL;

            if (strlen(filename) == 0)
            {
                free(filename);
                filename = strdup(defaultFilename);
            }
        }
        else
        {
            char tempString[256]; // Allocate buffer on stack with sufficient size
            sprintf(tempString, "Enter the %s filename: ", promptMsg);
            filename = getString(tempString);
            if (filename == NULL || strlen(filename) == 0)
                return NULL;
        }

        // Process filename
        filename = processPath(filename);

        // Check if file exists
        if (!fileExists(filename))
        {
            printf("Error: File not found\n");
            free(filename);
            return NULL;
        }

        // Read file content
        keyContent = readFileContent(filename, &keyContentLength);
        if (keyContent == NULL)
        {
            printf("Error: Failed to read key file\n");
            free(filename);
            return NULL;
        }

        printf("%s: %.20s...\n", promptMsg, keyContent);
        free(filename);
    }

    return keyContent;
}

bool handleFileOutput(const char *content, size_t contentLength, bool isBinary)
{
    char *filename = getString("Enter the output filename: ");
    if (filename == NULL || strlen(filename) == 0)
        return false;

    // Process filename
    filename = processPath(filename);

    // If file does not exist, create it
    if (!fileExists(filename))
    {
        FILE *file = fopen(filename, "w");
        if (file == NULL)
        {
            printf("Error: Failed to create output file\n");
            free(filename);
            return false;
        }
        fclose(file);
    }

    printf("Output path: %s\n", filename);

    // Save output to file
    FILE *file = fopen(filename, "wb");
    if (file == NULL)
    {
        printf("Error: Failed to open output file for writing\n");
        free(filename);
        return false;
    }

    size_t bytesWritten = fwrite(content, 1, contentLength, file);
    if (bytesWritten != contentLength)
    {
        printf("Error: Failed to write all data to output file\n");
    }
    fclose(file);
    printf("Content saved to %s\n", filename);
    free(filename);
    return true;
}

void encryptHandler()
{
    printf("Encrypt handler\n");

    const char *methodTitle = "Choose an encryption method:";
    const char *methodOptions[] = {
        "Public-private key",
        "Symmetric key",
        "Back"};

    const char *inputTitle = "Choose an input source:";
    const char *inputOptions[] = {
        "From file",
        "From text",
        "Back"};

    const char *outputTitle = "Choose an output destination:";
    const char *outputOptions[] = {
        "To file",
        "To text",
        "Back"};

    const char *keyTitle = "Choose a key source:";
    const char *keySourceOptions[] = {
        "From file",
        "From text",
        "Back"};

    int encryptionMethod = getMenuSelection(methodTitle, methodOptions, sizeof(methodOptions) / sizeof(methodOptions[0]), true);
    if (encryptionMethod == 2)
        return;

    int inputMethod = getMenuSelection(inputTitle, inputOptions, sizeof(inputOptions) / sizeof(inputOptions[0]), true);
    if (inputMethod == 2)
        return;

    int outputMethod = getMenuSelection(outputTitle, outputOptions, sizeof(outputOptions) / sizeof(outputOptions[0]), true);
    if (outputMethod == 2)
        return;

    int keySource = getMenuSelection(keyTitle, keySourceOptions, sizeof(keySourceOptions) / sizeof(keySourceOptions[0]), true);
    if (keySource == 2)
        return;

    char *content = NULL; // Will hold either file content or user text
    size_t contentLength = 0;
    char *binaryOutput = NULL;
    size_t binaryOutputLength = 0;
    char *base64Output = NULL;
    size_t base64OutputLength = 0;

    if (inputMethod == 0) // From file
    {
        char *filename = getString("Enter the input filename: ");
        if (filename == NULL || strlen(filename) == 0)
            return;

        // Process filename
        filename = processPath(filename);

        // Check if file exists
        if (!fileExists(filename))
        {
            printf("Error: File not found\n");
            free(filename);
            return;
        }

        // Read file content using the new function
        content = readFileContent(filename, &contentLength);
        if (content == NULL)
        {
            free(filename);
            return;
        }

        // Display file contents
        printf("File contents:\n%s\n", content);

        free(filename);
    }
    else if (inputMethod == 1) // From text
    {
        content = getString("Enter the input text: ");
        if (content == NULL || strlen(content) == 0)
            return;

        contentLength = strlen(content);
        printf("Text: %s\n", content);
    }

    // Now you can use 'content' variable here regardless of input method
    if (content == NULL)
    {
        printf("Error: Unexpected error: Content is NULL\n");
        system("pause");
        return;
    }

    printf("Processing content with length: %zu\n", contentLength);

    if (encryptionMethod == 0) // Public-private key
    {
        // Get the public key - use the helper function
        char *keyContent = getKeyContent(keySource, "pubkey.pem", "public key");
        if (keyContent == NULL)
        {
            free(content);
            return;
        }
        size_t keyContentLength = strlen(keyContent);

        publicPrivateKeyEncryption(content, contentLength, &binaryOutput, &binaryOutputLength, &base64Output, &base64OutputLength, keyContent, keyContentLength);
        free(keyContent);

        // Use base64Output and base64OutputLength as needed
        if (base64Output != NULL)
        {
            printf("Encrypted content (Base64, first 50 characters):\n%.50s...\n", base64Output);
        }
    }
    else if (encryptionMethod == 1) // Symmetric key
    {
        // Get the symmetric key - use the helper function
        char *keyContent = getKeyContent(keySource, NULL, "symmetric key");
        if (keyContent == NULL)
        {
            free(content);
            return;
        }
        size_t keyContentLength = strlen(keyContent);

        symmetricKeyEncryption(content, contentLength, &binaryOutput, &binaryOutputLength,
                               &base64Output, &base64OutputLength, keyContent, keyContentLength);
        free(keyContent);

        // Use base64Output and base64OutputLength as needed
        if (base64Output != NULL)
        {
            printf("Encrypted content (Base64, first 50 characters):\n%.50s...\n", base64Output);
        }
    }

    // Free content when done
    free(content);

    // Handle output based on the selected output method
    if (outputMethod == 0) // To file
    {
        if (!handleFileOutput(binaryOutput, binaryOutputLength, true))
        {
            free(binaryOutput);
            free(base64Output);
            return;
        }
    }
    else if (outputMethod == 1) // To text
    {
        printf("Encrypted content:\n%s\n", base64Output);
    }

    // Free outputs when done
    free(binaryOutput);
    free(base64Output);
}

// Implement the symmetricKeyEncryption function
void symmetricKeyEncryption(const char *content, size_t contentLength,
                            char **binaryOutput, size_t *binaryOutputLength,
                            char **base64Output, size_t *base64OutputLength,
                            const char *keyContent, size_t keyContentLength)
{
    // Create an initialization vector (IV)
    unsigned char iv[AES_BLOCK_SIZE];
    if (RAND_bytes(iv, AES_BLOCK_SIZE) != 1)
    {
        printf("Error: Failed to generate random IV\n");
        return;
    }

    // Generate a 256-bit key from the provided key content using SHA-256
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    unsigned char key[EVP_MAX_KEY_LENGTH];
    unsigned int key_len;

    if (!mdctx)
    {
        printf("Error: Failed to create message digest context\n");
        return;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1)
    {
        printf("Error: Failed to initialize digest\n");
        EVP_MD_CTX_free(mdctx);
        return;
    }

    if (EVP_DigestUpdate(mdctx, keyContent, keyContentLength) != 1)
    {
        printf("Error: Failed to update digest\n");
        EVP_MD_CTX_free(mdctx);
        return;
    }

    if (EVP_DigestFinal_ex(mdctx, key, &key_len) != 1)
    {
        printf("Error: Failed to finalize digest\n");
        EVP_MD_CTX_free(mdctx);
        return;
    }

    EVP_MD_CTX_free(mdctx);

    // Prepare for encryption
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx)
    {
        printf("Error: Failed to create cipher context\n");
        return;
    }

    // Initialize the encryption operation with AES-256-CBC
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv) != 1)
    {
        printf("Error: Failed to initialize encryption\n");
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    // Prepare output buffer (may be larger than input due to padding)
    int maxOutputLen = contentLength + AES_BLOCK_SIZE;
    unsigned char *encryptedContent = (unsigned char *)malloc(maxOutputLen + AES_BLOCK_SIZE); // Extra space for IV
    if (!encryptedContent)
    {
        printf("Error: Memory allocation failed\n");
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    // Copy IV to the beginning of the output
    memcpy(encryptedContent, iv, AES_BLOCK_SIZE);

    int len = 0, ciphertext_len = 0;

    // Encrypt the content
    if (EVP_EncryptUpdate(ctx, encryptedContent + AES_BLOCK_SIZE, &len,
                          (const unsigned char *)content, contentLength) != 1)
    {
        printf("Error: Encryption failed\n");
        free(encryptedContent);
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    ciphertext_len = len;

    // Finalize the encryption (handle padding)
    if (EVP_EncryptFinal_ex(ctx, encryptedContent + AES_BLOCK_SIZE + len, &len) != 1)
    {
        printf("Error: Failed to finalize encryption\n");
        free(encryptedContent);
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    ciphertext_len += len;

    // Set output binary data (IV + ciphertext)
    *binaryOutputLength = AES_BLOCK_SIZE + ciphertext_len;
    *binaryOutput = (char *)malloc(*binaryOutputLength);
    if (!*binaryOutput)
    {
        printf("Error: Memory allocation failed\n");
        free(encryptedContent);
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    memcpy(*binaryOutput, encryptedContent, *binaryOutputLength);

    // Base64 encode the encrypted data (IV + ciphertext)
    BIO *b64 = BIO_new(BIO_f_base64());
    BIO *mem = BIO_new(BIO_s_mem());
    if (!b64 || !mem)
    {
        printf("Error: Failed to create BIOs for Base64 encoding\n");
        free(encryptedContent);
        free(*binaryOutput);
        *binaryOutput = NULL;
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    BIO_push(b64, mem);
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    BIO_write(b64, encryptedContent, *binaryOutputLength);
    BIO_flush(b64);

    // Get base64 encoded data
    BUF_MEM *bptr;
    BIO_get_mem_ptr(mem, &bptr);

    // Allocate memory for base64 output (add space for null terminator)
    *base64Output = (char *)malloc(bptr->length + 1);
    if (*base64Output == NULL)
    {
        printf("Error: Memory allocation for base64 output failed\n");
        free(encryptedContent);
        free(*binaryOutput);
        *binaryOutput = NULL;
        BIO_free_all(b64);
        EVP_CIPHER_CTX_free(ctx);
        return;
    }

    // Copy base64 data to output
    memcpy(*base64Output, bptr->data, bptr->length);
    (*base64Output)[bptr->length] = '\0';
    *base64OutputLength = bptr->length;

    // Clean up
    free(encryptedContent);
    BIO_free_all(b64); // This also frees 'mem'
    EVP_CIPHER_CTX_free(ctx);
}

// Implement the symmetricKeyDecryption function
void symmetricKeyDecryption(const char *content, size_t contentLength,
                            char **decryptedOutput, size_t *decryptedOutputLength,
                            const char *keyContent, size_t keyContentLength,
                            bool isBase64Input)
{
    unsigned char *binaryInput = NULL;
    size_t binaryInputLength = 0;

    // If input is Base64 encoded, decode it first
    if (isBase64Input)
    {
        BIO *b64 = BIO_new(BIO_f_base64());
        BIO *mem = BIO_new_mem_buf((void *)content, contentLength);
        if (!b64 || !mem)
        {
            printf("Error: Failed to create BIOs for Base64 decoding\n");
            return;
        }

        BIO_push(b64, mem);
        BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);

        // Allocate memory for decoded data (will be smaller than encoded)
        binaryInput = (unsigned char *)malloc(contentLength);
        if (binaryInput == NULL)
        {
            printf("Error: Memory allocation for decoded data failed\n");
            BIO_free_all(b64);
            return;
        }

        binaryInputLength = BIO_read(b64, binaryInput, contentLength);
        BIO_free_all(b64);

        if (binaryInputLength <= 0)
        {
            printf("Error: Base64 decoding failed\n");
            free(binaryInput);
            return;
        }
    }
    else
    {
        // If input is already binary, just use it directly
        binaryInput = (unsigned char *)malloc(contentLength);
        if (binaryInput == NULL)
        {
            printf("Error: Memory allocation failed\n");
            return;
        }

        memcpy(binaryInput, content, contentLength);
        binaryInputLength = contentLength;
    }

    // Ensure we have at least enough bytes for the IV
    if (binaryInputLength < AES_BLOCK_SIZE)
    {
        printf("Error: Input data too short to contain IV\n");
        free(binaryInput);
        return;
    }

    // Extract IV from the beginning of the input
    unsigned char iv[AES_BLOCK_SIZE];
    memcpy(iv, binaryInput, AES_BLOCK_SIZE);

    // Generate a 256-bit key from the provided key content using SHA-256
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    unsigned char key[EVP_MAX_KEY_LENGTH];
    unsigned int key_len;

    if (!mdctx)
    {
        printf("Error: Failed to create message digest context\n");
        free(binaryInput);
        return;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1)
    {
        printf("Error: Failed to initialize digest\n");
        EVP_MD_CTX_free(mdctx);
        free(binaryInput);
        return;
    }

    if (EVP_DigestUpdate(mdctx, keyContent, keyContentLength) != 1)
    {
        printf("Error: Failed to update digest\n");
        EVP_MD_CTX_free(mdctx);
        free(binaryInput);
        return;
    }

    if (EVP_DigestFinal_ex(mdctx, key, &key_len) != 1)
    {
        printf("Error: Failed to finalize digest\n");
        EVP_MD_CTX_free(mdctx);
        free(binaryInput);
        return;
    }

    EVP_MD_CTX_free(mdctx);

    // Prepare for decryption
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx)
    {
        printf("Error: Failed to create cipher context\n");
        free(binaryInput);
        return;
    }

    // Initialize the decryption operation with AES-256-CBC
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv) != 1)
    {
        printf("Error: Failed to initialize decryption\n");
        EVP_CIPHER_CTX_free(ctx);
        free(binaryInput);
        return;
    }

    // Allocate memory for plaintext (will be at most as large as the ciphertext)
    *decryptedOutput = (char *)malloc(binaryInputLength);
    if (*decryptedOutput == NULL)
    {
        printf("Error: Memory allocation failed\n");
        EVP_CIPHER_CTX_free(ctx);
        free(binaryInput);
        return;
    }

    int len = 0, plaintext_len = 0;

    // Decrypt the content (skip the IV)
    if (EVP_DecryptUpdate(ctx, (unsigned char *)*decryptedOutput, &len,
                          binaryInput + AES_BLOCK_SIZE, binaryInputLength - AES_BLOCK_SIZE) != 1)
    {
        printf("Error: Decryption failed\n");
        free(*decryptedOutput);
        *decryptedOutput = NULL;
        EVP_CIPHER_CTX_free(ctx);
        free(binaryInput);
        return;
    }

    plaintext_len = len;

    // Finalize the decryption (handle padding)
    if (EVP_DecryptFinal_ex(ctx, (unsigned char *)*decryptedOutput + len, &len) != 1)
    {
        printf("Error: Failed to finalize decryption\n");
        free(*decryptedOutput);
        *decryptedOutput = NULL;
        EVP_CIPHER_CTX_free(ctx);
        free(binaryInput);
        return;
    }

    plaintext_len += len;

    // Add null terminator
    (*decryptedOutput)[plaintext_len] = '\0';
    *decryptedOutputLength = plaintext_len;

    // Clean up
    EVP_CIPHER_CTX_free(ctx);
    free(binaryInput);
}

void decryptHandler()
{
    printf("Decrypt handler\n");

    const char *methodTitle = "Choose a decryption method:";
    const char *methodOptions[] = {
        "Public-private key",
        "Symmetric key",
        "Back"};
    const char *inputTitle = "Choose an input source:";
    const char *inputOptions[] = {
        "From file",
        "From text",
        "Back"};
    const char *outputTitle = "Choose an output destination:";
    const char *outputOptions[] = {
        "To file",
        "To text",
        "Back"};
    const char *keySourceTitle = "Choose a key source:";
    const char *keySourceOptions[] = {
        "From file",
        "From text",
        "Back"};
    const char *formatTitle = "Select input format:";
    const char *formatOptions[] = {
        "Base64 encoded",
        "Binary",
        "Back"};

    int decryptionMethod = getMenuSelection(methodTitle, methodOptions, sizeof(methodOptions) / sizeof(methodOptions[0]), true);
    if (decryptionMethod == 2)
        return;

    int inputMethod = getMenuSelection(inputTitle, inputOptions, sizeof(inputOptions) / sizeof(inputOptions[0]), true);
    if (inputMethod == 2)
        return;

    int outputMethod = getMenuSelection(outputTitle, outputOptions, sizeof(outputOptions) / sizeof(outputOptions[0]), true);
    if (outputMethod == 2)
        return;

    int keySource = getMenuSelection(keySourceTitle, keySourceOptions, sizeof(keySourceOptions) / sizeof(keySourceOptions[0]), true);
    if (keySource == 2)
        return;

    char *content = NULL; // Will hold either file content or user text
    size_t contentLength = 0;

    if (inputMethod == 0) // From file
    {
        char *filename = getString("Enter the input filename: ");
        if (filename == NULL || strlen(filename) == 0)
            return;

        // Process filename
        filename = processPath(filename);

        // Check if file exists
        if (!fileExists(filename))
        {
            printf("Error: File not found\n");
            free(filename);
            return;
        }

        // Read file content using the new function
        content = readFileContent(filename, &contentLength);
        if (content == NULL)
        {
            free(filename);
            return;
        }

        // Display file contents
        printf("File contents:\n%s\n", content);

        free(filename);
    }
    else if (inputMethod == 1) // From text
    {
        content = getString("Enter the input text: ");
        if (content == NULL || strlen(content) == 0)
            return;

        contentLength = strlen(content);
        printf("Text: %s\n", content);
    }

    // Now you can use 'content' variable here regardless of input method
    if (content == NULL)
    {
        printf("Error: Unexpected error: Content is NULL\n");
        system("pause");
        return;
    }
    printf("Processing content with length: %zu\n", contentLength);

    // Determine if input is Base64 encoded or binary
    int formatChoice = getMenuSelection(formatTitle, formatOptions, sizeof(formatOptions) / sizeof(formatOptions[0]), true);
    if (formatChoice == 2)
    {
        free(content);
        return;
    }
    bool isBase64Input = (formatChoice == 0);

    // Get the appropriate key content based on decryption method
    char *keyContent = NULL;
    const char *defaultFilename = NULL;
    const char *promptMsg = NULL;

    if (decryptionMethod == 0) // Public-private key
    {
        defaultFilename = "privkey.pem";
        promptMsg = "private key";
    }
    else if (decryptionMethod == 1) // Symmetric key
    {
        defaultFilename = NULL;
        promptMsg = "symmetric key";
    }

    keyContent = getKeyContent(keySource, defaultFilename, promptMsg);
    if (keyContent == NULL)
    {
        free(content);
        return;
    }
    size_t keyContentLength = strlen(keyContent);

    // Process decryption based on the selected method
    char *decryptedOutput = NULL;
    size_t decryptedOutputLength = 0;

    if (decryptionMethod == 0) // Public-private key
    {
        publicPrivateKeyDecryption(content, contentLength, &decryptedOutput, &decryptedOutputLength,
                                  keyContent, keyContentLength, isBase64Input);
    }
    else if (decryptionMethod == 1) // Symmetric key
    {
        symmetricKeyDecryption(content, contentLength, &decryptedOutput, &decryptedOutputLength,
                              keyContent, keyContentLength, isBase64Input);
    }

    // Clean up key content when done
    free(keyContent);
    // Clean up input content when done
    free(content);

    // Handle output if decryption was successful
    if (decryptedOutput != NULL)
    {
        if (outputMethod == 0) // To file
        {
            if (!handleFileOutput(decryptedOutput, decryptedOutputLength, false))
            {
                free(decryptedOutput);
                return;
            }
        }
        else if (outputMethod == 1) // To text
        {
            printf("Decrypted content:\n%s\n", decryptedOutput);
        }

        // Clean up decrypted output when done
        free(decryptedOutput);
    }
}

void publicPrivateKeyEncryption(const char *content, size_t contentLength,
                                char **binaryOutput, size_t *binaryOutputLength,
                                char **base64Output, size_t *base64OutputLength,
                                const char *pubKeyContent, size_t pubKeyContentLength)
{
    // Load public key from PEM format
    BIO *bio = BIO_new_mem_buf((void *)pubKeyContent, pubKeyContentLength);
    if (!bio)
    {
        printf("Error: Failed to create BIO\n");
        return;
    }

    EVP_PKEY *pkey = PEM_read_bio_PUBKEY(bio, NULL, NULL, NULL);
    if (pkey == NULL)
    {
        printf("Error: Failed to load public key\n");
        BIO_free(bio);
        return;
    }

    // Create the cipher context for encryption
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new(pkey, NULL);
    if (!ctx)
    {
        printf("Error: Failed to create encryption context\n");
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Initialize for encryption
    if (EVP_PKEY_encrypt_init(ctx) <= 0)
    {
        printf("Error: Encryption initialization failed\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Set padding mode to OAEP (same as RSA_PKCS1_OAEP_PADDING)
    if (EVP_PKEY_CTX_set_rsa_padding(ctx, RSA_PKCS1_OAEP_PADDING) <= 0)
    {
        printf("Error: Failed to set padding\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Determine output buffer size
    size_t outlen;
    if (EVP_PKEY_encrypt(ctx, NULL, &outlen, (const unsigned char *)content, contentLength) <= 0)
    {
        printf("Error: Failed to determine output length\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Allocate memory for encrypted data
    *binaryOutput = (char *)malloc(outlen);
    if (*binaryOutput == NULL)
    {
        printf("Error: Memory allocation failed\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Perform encryption
    if (EVP_PKEY_encrypt(ctx, (unsigned char *)*binaryOutput, &outlen,
                         (const unsigned char *)content, contentLength) <= 0)
    {
        printf("Error: Encryption failed\n");
        free(*binaryOutput);
        *binaryOutput = NULL;
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    *binaryOutputLength = outlen;

    // Base64 encode the encrypted data - this part remains the same
    BIO *b64 = BIO_new(BIO_f_base64());
    BIO *mem = BIO_new(BIO_s_mem());
    if (!b64 || !mem)
    {
        printf("Error: Failed to create BIOs for Base64 encoding\n");
        free(*binaryOutput);
        *binaryOutput = NULL;
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    BIO_push(b64, mem);
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    BIO_write(b64, *binaryOutput, outlen);
    BIO_flush(b64);

    // Get base64 encoded data
    BUF_MEM *bptr;
    BIO_get_mem_ptr(mem, &bptr);

    // Allocate memory for base64 output (add space for null terminator)
    *base64Output = (char *)malloc(bptr->length + 1);
    if (*base64Output == NULL)
    {
        printf("Error: Memory allocation for base64 output failed\n");
        free(*binaryOutput);
        *binaryOutput = NULL;
        BIO_free_all(b64);
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        return;
    }

    // Copy base64 data to output
    memcpy(*base64Output, bptr->data, bptr->length);
    (*base64Output)[bptr->length] = '\0';
    *base64OutputLength = bptr->length;

    // Clean up
    BIO_free_all(b64); // This also frees 'mem'
    EVP_PKEY_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    BIO_free(bio);
}

void publicPrivateKeyDecryption(const char *content, size_t contentLength,
                                char **decryptedOutput, size_t *decryptedOutputLength,
                                const char *privKeyContent, size_t privKeyContentLength,
                                bool isBase64Input)
{
    unsigned char *binaryInput = NULL;
    size_t binaryInputLength = 0;

    // If input is Base64 encoded, decode it first
    if (isBase64Input)
    {
        BIO *b64 = BIO_new(BIO_f_base64());
        BIO *mem = BIO_new_mem_buf((void *)content, contentLength);
        if (!b64 || !mem)
        {
            printf("Error: Failed to create BIOs for Base64 decoding\n");
            return;
        }

        BIO_push(b64, mem);
        BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);

        // Allocate memory for decoded data (will be smaller than encoded)
        binaryInput = (unsigned char *)malloc(contentLength);
        if (binaryInput == NULL)
        {
            printf("Error: Memory allocation for decoded data failed\n");
            BIO_free_all(b64);
            return;
        }

        binaryInputLength = BIO_read(b64, binaryInput, contentLength);
        BIO_free_all(b64);

        if (binaryInputLength <= 0)
        {
            printf("Error: Base64 decoding failed\n");
            free(binaryInput);
            return;
        }
    }
    else
    {
        // If input is already binary, just use it directly
        binaryInput = (unsigned char *)malloc(contentLength);
        if (binaryInput == NULL)
        {
            printf("Error: Memory allocation failed\n");
            return;
        }

        memcpy(binaryInput, content, contentLength);
        binaryInputLength = contentLength;
    }

    // Load private key from PEM format
    BIO *bio = BIO_new_mem_buf((void *)privKeyContent, privKeyContentLength);
    if (!bio)
    {
        printf("Error: Failed to create BIO\n");
        free(binaryInput);
        return;
    }

    EVP_PKEY *pkey = PEM_read_bio_PrivateKey(bio, NULL, NULL, NULL);
    if (pkey == NULL)
    {
        printf("Error: Failed to load private key\n");
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Create the cipher context for decryption
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new(pkey, NULL);
    if (!ctx)
    {
        printf("Error: Failed to create decryption context\n");
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Initialize for decryption
    if (EVP_PKEY_decrypt_init(ctx) <= 0)
    {
        printf("Error: Decryption initialization failed\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Set padding mode to OAEP (same as used in encryption)
    if (EVP_PKEY_CTX_set_rsa_padding(ctx, RSA_PKCS1_OAEP_PADDING) <= 0)
    {
        printf("Error: Failed to set padding\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Determine output buffer size
    size_t outlen;
    if (EVP_PKEY_decrypt(ctx, NULL, &outlen, binaryInput, binaryInputLength) <= 0)
    {
        printf("Error: Failed to determine output length\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Allocate memory for decrypted data
    *decryptedOutput = (char *)malloc(outlen + 1); // +1 for null terminator
    if (*decryptedOutput == NULL)
    {
        printf("Error: Memory allocation failed\n");
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Perform decryption
    if (EVP_PKEY_decrypt(ctx, (unsigned char *)*decryptedOutput, &outlen,
                         binaryInput, binaryInputLength) <= 0)
    {
        printf("Error: Decryption failed\n");
        free(*decryptedOutput);
        *decryptedOutput = NULL;
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pkey);
        BIO_free(bio);
        free(binaryInput);
        return;
    }

    // Add null terminator to make it a proper string
    (*decryptedOutput)[outlen] = '\0';
    *decryptedOutputLength = outlen;

    // Clean up
    free(binaryInput);
    EVP_PKEY_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    BIO_free(bio);
}

void generateKeyHandler()
{
    printf("Generate key handler\n");

    char *pubKeyFilename = getString("Enter the public key filename [pubkey.pem]: ");
    if (pubKeyFilename == NULL || strlen(pubKeyFilename) == 0)
        pubKeyFilename = strdup("pubkey.pem");
    char *privKeyFilename = getString("Enter the private key filename [privkey.pem]: ");
    if (privKeyFilename == NULL || strlen(privKeyFilename) == 0)
        privKeyFilename = strdup("privkey.pem");

    // Generate RSA key pair using EVP interface
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, NULL);

    if (!ctx)
    {
        printf("Error: Failed to create key generation context\n");
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    if (EVP_PKEY_keygen_init(ctx) <= 0)
    {
        printf("Error: Failed to initialize key generation\n");
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    // Set RSA key length to 2048 bits
    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0)
    {
        printf("Error: Failed to set key length\n");
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    // Generate the key
    if (EVP_PKEY_keygen(ctx, &pkey) <= 0)
    {
        printf("Error: Failed to generate RSA key pair\n");
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    // Save public key to file
    FILE *pubKeyFile = fopen(pubKeyFilename, "wb");
    if (pubKeyFile == NULL)
    {
        printf("Error: Failed to open public key file for writing\n");
        EVP_PKEY_free(pkey);
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    if (PEM_write_PUBKEY(pubKeyFile, pkey) != 1)
    {
        printf("Error: Failed to write public key to file\n");
        fclose(pubKeyFile);
        EVP_PKEY_free(pkey);
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }
    fclose(pubKeyFile);

    // Save private key to file
    FILE *privKeyFile = fopen(privKeyFilename, "wb");
    if (privKeyFile == NULL)
    {
        printf("Error: Failed to open private key file for writing\n");
        EVP_PKEY_free(pkey);
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }

    if (PEM_write_PrivateKey(privKeyFile, pkey, NULL, NULL, 0, NULL, NULL) != 1)
    {
        printf("Error: Failed to write private key to file\n");
        fclose(privKeyFile);
        EVP_PKEY_free(pkey);
        EVP_PKEY_CTX_free(ctx);
        free(pubKeyFilename);
        free(privKeyFilename);
        return;
    }
    fclose(privKeyFile);

    // Clean up
    EVP_PKEY_free(pkey);
    EVP_PKEY_CTX_free(ctx);
    printf("RSA key pair generated and saved to %s and %s\n", pubKeyFilename, privKeyFilename);
    free(pubKeyFilename);
    free(privKeyFilename);
}

void hashHandler()
{
    printf("Hash handler\n");

    const char *inputTitle = "Choose an input source:";
    const char *inputOptions[] = {
        "From file",
        "From text",
        "Back"};

    const char *outputTitle = "Choose an output destination:";
    const char *outputOptions[] = {
        "To file",
        "To text",
        "Back"};

    const char *hashTitle = "Choose a hash algorithm:";
    const char *hashOptions[] = {
        "SHA256",
        "SHA512",
        "MD5",
        "Back"};

    int inputMethod = getMenuSelection(inputTitle, inputOptions, sizeof(inputOptions) / sizeof(inputOptions[0]), true);
    if (inputMethod == 2)
        return;

    int outputMethod = getMenuSelection(outputTitle, outputOptions, sizeof(outputOptions) / sizeof(outputOptions[0]), true);
    if (outputMethod == 2)
        return;

    int hashMethod = getMenuSelection(hashTitle, hashOptions, sizeof(hashOptions) / sizeof(hashOptions[0]), true);
    if (hashMethod == 3)
        return;

    char *content = NULL; // Will hold either file content or user text
    size_t contentLength = 0;
    char *hashOutput = NULL; // Will hold the hash output
    size_t hashOutputLength = 0;
    char *filename = NULL;

    if (inputMethod == 0) // From file
    {
        filename = getString("Enter the input filename: ");
        if (filename == NULL || strlen(filename) == 0)
            return;

        // Process filename
        filename = processPath(filename);

        // Check if file exists
        if (!fileExists(filename))
        {
            printf("Error: File not found\n");
            free(filename);
            return;
        }

        // Read file content using the new function
        content = readFileContent(filename, &contentLength);
        if (content == NULL)
        {
            free(filename);
            return;
        }

        // Display file contents
        printf("File contents:\n%s\n", content);

        free(filename);
    }
    else if (inputMethod == 1) // From text
    {
        content = getString("Enter the input text: ");
        if (content == NULL || strlen(content) == 0)
            return;

        contentLength = strlen(content);
        printf("Text: %s\n", content);
    }

    // Now you can use 'content' variable here regardless of input method
    if (content == NULL)
    {
        printf("Error: Unexpected error: Content is NULL\n");
        system("pause");
        return;
    }
    printf("Processing content with length: %zu\n", contentLength);

    // Hash the content
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md = NULL;
    switch (hashMethod)
    {
    case 0: // SHA256
        md = EVP_sha256();
        break;
    case 1: // SHA512
        md = EVP_sha512();
        break;
    case 2: // MD5
        md = EVP_md5();
        break;
    default:
        printf("Error: Invalid hash method\n");
        EVP_MD_CTX_free(mdctx);
        free(content);
        return;
    }

    if (!mdctx)
    {
        printf("Error: Failed to create message digest context\n");
        free(content);
        return;
    }

    if (EVP_DigestInit_ex(mdctx, md, NULL) != 1)
    {
        printf("Error: Failed to initialize digest\n");
        EVP_MD_CTX_free(mdctx);
        free(content);
        return;
    }

    if (EVP_DigestUpdate(mdctx, content, contentLength) != 1)
    {
        printf("Error: Failed to update digest\n");
        EVP_MD_CTX_free(mdctx);
        free(content);
        return;
    }

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        printf("Error: Failed to finalize digest\n");
        EVP_MD_CTX_free(mdctx);
        free(content);
        return;
    }

    EVP_MD_CTX_free(mdctx);
    free(content);
    content = NULL; // Clear content after hashing
    contentLength = 0; // Clear content length
    hashOutputLength = hash_len * 2 + 1; // Each byte is represented by 2 hex characters + null terminator
    hashOutput = (char *)malloc(hashOutputLength);
    if (hashOutput == NULL)
    {
        printf("Error: Memory allocation for hash output failed\n");
        return;
    }
    for (size_t i = 0; i < hash_len; i++)
    {
        sprintf(hashOutput + (i * 2), "%02x", hash[i]);
    }
    hashOutput[hashOutputLength - 1] = '\0'; // Null-terminate the string
    printf("Hash output: %s\n", hashOutput);
    // Handle the hash output
    if (outputMethod == 0) // To file
    {
        filename = getString("Enter the output filename: ");
        if (filename == NULL || strlen(filename) == 0)
        {
            free(hashOutput);
            return;
        }

        // Process filename
        filename = processPath(filename);

        // Check if file exists
        if (!fileExists(filename))
        {
            FILE *file = fopen(filename, "w");
            if (file == NULL)
            {
                printf("Error: Failed to create output file\n");
                free(filename);
                free(hashOutput);
                return;
            }
            fclose(file);
        }

        // Save output to file
        FILE *file = fopen(filename, "w");
        if (file == NULL)
        {
            printf("Error: Failed to open output file for writing\n");
            free(filename);
            free(hashOutput);
            return;
        }

        size_t bytesWritten = fwrite(hashOutput, 1, hashOutputLength - 1, file); // Exclude null terminator
        if (bytesWritten != hashOutputLength - 1)
        {
            printf("Error: Failed to write all data to output file\n");
        }
        fclose(file);
        printf("Hash output saved to %s\n", filename);
        free(filename);
    }
    else if (outputMethod == 1) // To text
    {
        printf("Hash output:\n%s\n", hashOutput);
    }
    free(hashOutput);
    hashOutput = NULL; // Clear hash output after use
    hashOutputLength = 0; // Clear hash output length
}