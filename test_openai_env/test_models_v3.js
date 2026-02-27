
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
            messages: [{ role: "user", content: "Hello" }],
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
    // 1. Try gemini-2.5-flash (Newest!)
    await testModel("gemini-2.5-flash");

    // 2. Try gemini-2.0-flash-lite-001 (Lite might have diff quota)
    await testModel("gemini-2.0-flash-lite-001");

    // 3. Try gemini-flash-lite-latest (Another alias)
    await testModel("gemini-flash-lite-latest");
}

main();
