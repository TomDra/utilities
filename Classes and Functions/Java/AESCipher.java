import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.security.spec.KeySpec;
import java.util.Base64;

public class AESCipher {

    private final SecretKey secretKey;

    public AESCipher(byte[] password, byte[] salt, int iterations) throws Exception {
        this.secretKey = deriveKey(password, salt, iterations);
    }

    private SecretKey deriveKey(byte[] password, byte[] salt, int iterations) throws Exception {
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        KeySpec spec = new PBEKeySpec(
                new String(password).toCharArray(),
                salt,
                iterations,
                256
        );
        SecretKey tmp = factory.generateSecret(spec);
        return new SecretKeySpec(tmp.getEncoded(), "AES");
    }

    public String encrypt(byte[] plaintext) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        byte[] iv = new byte[16];
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        IvParameterSpec ivSpec = new IvParameterSpec(iv);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec);
        byte[] encrypted = cipher.doFinal(plaintext);

        byte[] ivAndCiphertext = new byte[iv.length + encrypted.length];
        System.arraycopy(iv, 0, ivAndCiphertext, 0, iv.length);
        System.arraycopy(encrypted, 0, ivAndCiphertext, iv.length, encrypted.length);

        return Base64.getEncoder().encodeToString(ivAndCiphertext);
    }

    public byte[] decrypt(String encryptedData) throws Exception {
        byte[] decoded = Base64.getDecoder().decode(encryptedData);
        if (decoded.length < 16) {
            throw new IllegalArgumentException("Invalid encrypted data: too short for IV");
        }

        byte[] iv = new byte[16];
        byte[] ciphertext = new byte[decoded.length - 16];
        System.arraycopy(decoded, 0, iv, 0, 16);
        System.arraycopy(decoded, 16, ciphertext, 0, ciphertext.length);

        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, secretKey, new IvParameterSpec(iv));
        return cipher.doFinal(ciphertext);
    }

    // Example usage
    public static void main(String[] args) throws Exception {
        byte[] key = "08180230818209389012832132109123".getBytes();  // Not secure! Just for testing
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);

        AESCipher aes = new AESCipher(key, salt, 100_000);

        String original = "This is very secret data!";
        String encrypted = aes.encrypt(original.getBytes());
        System.out.println("Encrypted: " + encrypted);

        byte[] decrypted = aes.decrypt(encrypted);
        System.out.println("Decrypted: " + new String(decrypted));
    }
}
