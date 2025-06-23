type PipelineSession = {
  topic: string;
  pipeline_status: "queued" | "running" | "waiting_for_input" | "completed" | "failed";
  status: string;
  start_at: string;
  ended_at: string | null;
  updated_at: string;
  update: string | null;
  error: string | null;
  agent_updates: [];
  progress: number;
};

export type PipelineSessionStatus = PipelineSession;