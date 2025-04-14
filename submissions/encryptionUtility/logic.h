#ifndef LOGIC_H
#define LOGIC_H

#include <stdbool.h>
#include <stddef.h>

// Helper functions for common operations
char* getKeyContent(int keySource, const char* defaultFilename, const char* promptMsg);
bool handleFileOutput(const char* content, size_t contentLength, bool isBinary);

// Main handler functions
void encryptHandler();
void decryptHandler();
void generateKeyHandler();
void hashHandler();

// Encryption functions
void publicPrivateKeyEncryption(const char *content, size_t contentLength,
                                char **binaryOutput, size_t *binaryOutputLength,
                                char **base64Output, size_t *base64OutputLength,
                                const char *pubKeyContent, size_t pubKeyContentLength);

void symmetricKeyEncryption(const char *content, size_t contentLength,
                            char **binaryOutput, size_t *binaryOutputLength,
                            char **base64Output, size_t *base64OutputLength,
                            const char *keyContent, size_t keyContentLength);

// Decryption functions
void publicPrivateKeyDecryption(const char *content, size_t contentLength,
                               char **decryptedOutput, size_t *decryptedOutputLength,
                               const char *privKeyContent, size_t privKeyContentLength,
                               bool isBase64Input);

void symmetricKeyDecryption(const char *content, size_t contentLength,
                            char **decryptedOutput, size_t *decryptedOutputLength,
                            const char *keyContent, size_t keyContentLength,
                            bool isBase64Input);

#endif // LOGIC_H