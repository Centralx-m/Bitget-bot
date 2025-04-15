// BitgetBot.java
import com.vercel.function.Request;
import com.vercel.function.Response;
import com.vercel.function.VercelFunction;
import okhttp3.*;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class BitgetBot implements VercelFunction {

    // Configure these in Vercel environment variables
    private static final String API_KEY = System.getenv("BITGET_API_KEY");
    private static final String SECRET_KEY = System.getenv("BITGET_SECRET_KEY");
    private static final String PASSPHRASE = System.getenv("BITGET_PASSPHRASE");
    private static final String BASE_URL = "https://api.bitget.com";

    private final OkHttpClient client = new OkHttpClient();

    @Override
    public void handle(Request request, Response response) {
        try {
            String method = request.getMethod();
            
            if ("POST".equals(method)) {
                // Example trading logic
                Map<String, String> params = new HashMap<>();
                params.put("symbol", "BTCUSDT");
                params.put("side", "buy");
                params.put("orderType", "market");
                params.put("force", "normal");
                params.put("size", "0.001");
                
                String result = placeOrder(params);
                response.send(result);
            } else {
                response.send("Bitget Trading Bot Ready. Send POST request to trade.");
            }
        } catch (Exception e) {
            response.setStatusCode(500);
            response.send("Error: " + e.getMessage());
        }
    }

    private String placeOrder(Map<String, String> params) throws IOException {
        String path = "/api/mix/v1/order/placeOrder";
        String timestamp = Instant.now().toEpochMilli() + "";
        
        String queryString = buildQueryString(params);
        String sign = generateSign(timestamp, "POST", path, queryString);
        
        RequestBody body = RequestBody.create(
            queryString, 
            MediaType.parse("application/json")
        );
        
        Request request = new Request.Builder()
            .url(BASE_URL + path)
            .post(body)
            .addHeader("ACCESS-KEY", API_KEY)
            .addHeader("ACCESS-SIGN", sign)
            .addHeader("ACCESS-TIMESTAMP", timestamp)
            .addHeader("ACCESS-PASSPHRASE", PASSPHRASE)
            .addHeader("Content-Type", "application/json")
            .build();
            
        try (Response httpResponse = client.newCall(request).execute()) {
            return httpResponse.body().string();
        }
    }

    private String generateSign(String timestamp, String method, String path, String body) {
        try {
            String preHash = timestamp + method.toUpperCase() + path + body;
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            byte[] hash = mac.doFinal(preHash.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("Failed to generate signature", e);
        }
    }

    private String buildQueryString(Map<String, String> params) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : params.entrySet()) {
            if (!first) {
                sb.append(",");
            }
            sb.append("\"").append(entry.getKey()).append("\":\"").append(entry.getValue()).append("\"");
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }
                
