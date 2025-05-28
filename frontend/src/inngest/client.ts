import { Inngest } from "inngest";
import { env } from "~/env";

// Create a client to send and receive events
export const inngest = new Inngest({
  id: "ai-podcast-clipper-frontend",
  eventKey: env.INNGEST_EVENT_KEY,
});
