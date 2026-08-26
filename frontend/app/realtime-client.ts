export type RealtimeClient = {
  pc: RTCPeerConnection;
  dc: RTCDataChannel;
  audio: HTMLAudioElement;
  close: () => void;
};

export async function connectRealtime(
  conversationId: string,
  onEvent?: (event: any) => void,
): Promise<RealtimeClient> {
  const r = await fetch(`/api/realtime/sessions?conversation_id=${encodeURIComponent(conversationId)}`, {
    method: "POST",
    credentials: "include",
  });
  if (!r.ok) throw new Error(await r.text());
  const session = await r.json();

  const pc = new RTCPeerConnection();
  const audio = document.createElement("audio");
  audio.autoplay = true;
  pc.ontrack = e => { audio.srcObject = e.streams[0]; };

  const stream = await navigator.mediaDevices.getUserMedia({audio: true});
  stream.getTracks().forEach(track => pc.addTrack(track, stream));

  const dc = pc.createDataChannel("oai-events");
  let lastSequence = 0;

  dc.onmessage = e => {
    try {
      const event = JSON.parse(e.data);
      if (typeof event.sequence === "number") lastSequence = Math.max(lastSequence, event.sequence);
      onEvent?.(event);
    } catch {
      onEvent?.({type: "raw", data: e.data});
    }
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  // Send the SDP offer to our backend proxy. The backend performs the
  // provider-specific multipart/form-data request and keeps provider keys
  // off the browser. Never call the Realtime provider directly from here.
  const answer = await fetch(`/api/realtime/session`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/sdp",
    },
    body: offer.sdp || "",
  });
  if (!answer.ok) throw new Error(await answer.text());
  const answerType = answer.headers.get("content-type") || "";
  const answerBody = await answer.text();
  let answerSdp = answerBody;
  if (answerType.includes("application/json")) {
    try { answerSdp = JSON.parse(answerBody)?.sdp || ""; } catch {}
  }
  if (!answerSdp) throw new Error("Backend did not return a valid SDP answer");
  await pc.setRemoteDescription({type: "answer", sdp: answerSdp});

  const close = () => {
    stream.getTracks().forEach(t => t.stop());
    dc.close();
    pc.close();
  };

  void lastSequence;
  return {pc, dc, audio, close};
}
