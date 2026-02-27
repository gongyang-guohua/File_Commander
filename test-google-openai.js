
const OpenAI = require("openai");

// Configuration from current openclaw.json attempt
const baseURL = "https://generativelanguage.googleapis.com/v1beta/openai/";
const apiKey = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY";
const model = "gemini-1.5-flash";

const client = new OpenAI({
    apiKey: apiKey,
    baseURL: baseURL,
});

async function main() {
    console.log(`Testing Google OpenAI Compat Layer...`);
    console.log(`BaseURL: ${baseURL}`);
    console.log(`Model: ${model}`);

    try {
        const completion = await client.chat.completions.create({
            messages: [{ role: "user", content: "Hello, are you working?" }],
            model: model,
        });

        console.log("SUCCESS!");
        console.log("Response:", completion.choices[0].message.content);
    } catch (error) {
        console.error("FAILED");
        console.error("Status:", error.status);
        console.error("Message:", error.message);
        if (error.response) {
            console.error("Response data:", error.response.data);
        }
    }
}

main();
