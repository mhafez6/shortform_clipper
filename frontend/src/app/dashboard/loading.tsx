import { Loader2 } from "lucide-react";

const Loading = () => {
  return <div className="flex items-center justify-center gap-5 p-12">
    <Loader2 className="text-muted-foreground h-1/2 w-12 animate-spin" />
    <span className="ml-3 text-lg">Loading dashboard info ...</span>
  </div>;
};

export default Loading;
