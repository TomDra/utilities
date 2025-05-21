// AESCipher.js
const crypto = require('crypto');

class AESCipher {
  constructor(password, salt, iterations = 100000) {
    this.key = this.deriveKey(password, salt, iterations);
  }

  deriveKey(password, salt, iterations) {
    return crypto.pbkdf2Sync(password, salt, iterations, 32, 'sha256');
  }

  encrypt(plaintext) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', this.key, iv);

    const padded = this.pkcs7Pad(Buffer.from(plaintext));
    const ciphertext = Buffer.concat([cipher.update(padded), cipher.final()]);

    return Buffer.concat([iv, ciphertext]).toString('base64');
  }

  decrypt(encryptedBase64) {
    const raw = Buffer.from(encryptedBase64, 'base64');
    if (raw.length < 16) throw new Error('Invalid encrypted data');

    const iv = raw.slice(0, 16);
    const ciphertext = raw.slice(16);

    const decipher = crypto.createDecipheriv('aes-256-cbc', this.key, iv);
    const paddedPlaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
    return this.pkcs7Unpad(paddedPlaintext).toString();
  }

  pkcs7Pad(buffer) {
    const padLength = 16 - (buffer.length % 16);
    const padding = Buffer.alloc(padLength, padLength);
    return Buffer.concat([buffer, padding]);
  }

  pkcs7Unpad(buffer) {
    const padLength = buffer[buffer.length - 1];
    if (padLength > 16 || padLength === 0) throw new Error("Invalid padding");
    return buffer.slice(0, -padLength);
  }
}

// Example usage:
const password = '08180230818209389012832132109123';
const salt = crypto.randomBytes(16);

const aes = new AESCipher(password, salt);

const data = 'This is very secret data!';
const encrypted = aes.encrypt(data);
console.log('Encrypted:', encrypted);

const decrypted = aes.decrypt(encrypted);
console.log('Decrypted:', decrypted);
