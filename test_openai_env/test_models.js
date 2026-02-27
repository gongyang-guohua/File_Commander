
const OpenAI = require("openai");

const baseURL = "https://generativelanguage.googleapis.com/v1beta/openai/";
const apiKey = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"; // Masked

const client = new OpenAI({
    apiKey: apiKey,
    baseURL: baseURL,
});

async function testModel(modelId) {
    console.log(`\nTesting Model: ${modelId}...`);
    try {
        const completion = await client.chat.completions.create({
            messages: [{ role: "user", content: "Hello, reply with 'OK'." }],
            model: modelId,
        });
        console.log(`[${modelId}] SUCCESS!`);
        console.log("Response:", completion.choices[0].message.content);
        return true;
    } catch (error) {
        console.error(`[${modelId}] FAILED`);
        if (error.status) console.error("Status:", error.status);
        if (error.error && error.error.message) console.error("Message:", error.error.message);
        else console.error("Message:", error.message);
        return false;
    }
}

async function main() {
    // 1. Try gemini-flash-latest (Likely 1.5 Flash alias)
    await testModel("gemini-flash-latest");

    // 2. Try gemini-2.0-flash (Confirm it exists but maybe 429)
    await testModel("gemini-2.0-flash");

    // 3. Try gemini-2.0-flash-lite-001 (Maybe lightweight enough?)
    await testModel("gemini-2.0-flash-lite-001");
}

main();
