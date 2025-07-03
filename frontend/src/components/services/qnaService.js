    // src/services/qnaService.js
import apiClient from "./apiClient";

export async function fetchConversations(userId) {
    return await apiClient(`/q-and-a/${userId}`);
}

export async function createConversation(userId) {
    const payload = {
        UserID: userId,
        Title: "New Conversation",
        History: [],
    };
    console.log("Payload for createConversation:", payload);
    return await apiClient(`/q-and-a/conversations/new`, {
        method: "POST",
        body: payload,
    });
}

export async function deleteConversation(conversationId) {
    return await apiClient(`/q-and-a/conversations/${conversationId}`, {
        method: "DELETE",
    });
}

export async function renameConversation(conversationId, newName) {
    return await apiClient(`/q-and-a/conversations/${conversationId}/renameConversation`, {
        method: "PUT",
        body: { title: newName },
    });
}

export async function fetchMessages(conversationId) {
    return await apiClient(`/q-and-a/conversations/${conversationId}`);
}

export async function sendMessage(conversationId, text, isCrawl, extractedUrl, linkSpecific, topK) {
    const payload = {
        text,
        isCrawl,
        linkSpecific: linkSpecific || extractedUrl || "",
        topK,
        conversationsessionsID: conversationId
    }
    console.log("Payload for sendMessage:", payload);
    return await apiClient("/q-and-a/getResponse", {
        method: "POST",
        body: payload,
    });
}

export async function fetchLocationInformations(conversationId) {
    return await apiClient(`/q-and-a/conversations/${conversationId}/locations`);
}

export async function updateLocationInformations(conversationId, locations) {
    return await apiClient(`/q-and-a/conversations/${conversationId}/updateLocations`, {
        method: "PUT",
        body: locations ,
    });
}
