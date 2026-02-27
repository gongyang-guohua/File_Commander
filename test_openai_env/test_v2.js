
const OpenAI = require("openai");

// TRY 2: Remove 'openai/' from base URL, maybe the SDK adds it? 
// No, SDK adds 'chat/completions'. 
// Google docs say: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
// So my previous URL was correct if SDK only adds /chat/completions.
// BUT maybe 404 is because the MODEL ID is wrong for this endpoint?
// Let's try 'gemini-1.5-flash-latest' or just 'gemini-1.5-flash'.

const baseURL = "https://generativelanguage.googleapis.com/v1beta/openai/";
const apiKey = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"; // Masked
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
            messages: [{ role: "user", content: "Hello" }],
            model: model,
        });
        console.log("SUCCESS!");
        console.log(completion.choices[0].message.content);
    } catch (error) {
        console.error("FAILED 1 (standard)");
        console.error(error.message);
    }

    // TRY 3: What if the URL shouldn't have /openai/ ?
    // If I use v1beta, SDK adds /chat/completions -> v1beta/chat/completions (Wrong)

    // TRY 4: Manually construct URL using fetch to see what's going on
    try {
        console.log("Testing with raw fetch...");
        const url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions";
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: [{ role: "user", content: "Hello" }]
            })
        });

        if (!response.ok) {
            console.log(`Fetch Status: ${response.status} ${response.statusText}`);
            const text = await response.text();
            console.log(`Body: ${text}`);
        } else {
            const data = await response.json();
            console.log("Fetch SUCCESS!");
            console.log(data);
        }
    } catch (e) {
        console.log("Fetch Error: " + e.message);
    }
}

main();
