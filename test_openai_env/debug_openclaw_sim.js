
// Simulate OpenClaw's openai-completions logic
const OpenAI = require("openai");

const model = {
    id: "gemini-flash-lite-latest",
    provider: "openai-completions",
    baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai/",
    headers: {}
};

const apiKey = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"; // Masked

async function run() {
    console.log("Simulating OpenClaw OpenAI Completions Provider...");

    // Logic from createClient
    const client = new OpenAI({
        apiKey,
        baseURL: model.baseUrl,
        defaultHeaders: model.headers,
    });

    // Logic from buildParams (simplified)
    const messages = [{ role: "user", content: "Hello" }];
    const params = {
        model: model.id,
        messages,
        stream: true,
    };

    // Add compatibility params that OpenClaw adds by default
    // detectCompat defaults:
    // params.stream_options = { include_usage: true };
    // params.store = false;

    // Let's see if THESE cause the 404?

    console.log("Params:", JSON.stringify(params, null, 2));

    try {
        const stream = await client.chat.completions.create(params);
        console.log("Stream started...");
        for await (const chunk of stream) {
            process.stdout.write(chunk.choices[0]?.delta?.content || "");
        }
        console.log("\nDone.");
    } catch (e) {
        console.error("ERROR:", e.message);
        if (e.status) console.error("Status:", e.status);
    }
}

run();
