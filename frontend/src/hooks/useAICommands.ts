
import { useCommand, Operation } from "@/hooks/useCommand";
import { useToast } from "@/hooks/use-toast";
import { useEditorStore, Clip } from "@/store/editorStore";

export const useAICommands = () => {
  const { toast } = useToast();
  const { executeCommand } = useCommand("current-project");
  const { clips, selectedClipId, setClips, setSelectedClipId } = useEditorStore();

  const handleChatCommand = async (command: string) => {
    if (!selectedClipId && clips.length === 0) {
      toast({
        title: "No video available",
        description: "Please add a video to the timeline first",
        variant: "destructive",
      });
      return;
    }
    
    console.log("Processing command:", command);
    
    // Use our command hook to process the NLP request
    const result = await executeCommand(command);
    
    if (result && result.operations.length > 0) {
      // Apply the operations to the timeline
      applyOperationsToTimeline(result.operations);
      return result;
    }
    
    return null;
  };

  // Apply AI operations to the timeline
  const applyOperationsToTimeline = (operations: Operation[]) => {
    // Convert operations to clips
    const newClips = operations.map(op => {
      const clipId = `clip-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      
      return {
        id: clipId,
        start: op.start_sec,
        end: op.end_sec,
        track: determineTrackForEffect(op.effect),
        type: op.effect,
        name: `${op.effect.charAt(0).toUpperCase() + op.effect.slice(1)} Effect`
      };
    });
    
    // Preserve existing clips by merging them with new clips
    const updatedClips = [...clips, ...newClips];
    setClips(updatedClips);
    
    if (newClips.length > 0) {
      setSelectedClipId(newClips[0].id);
      
      toast({
        title: "Edits applied",
        description: `${newClips.length} operations added to timeline`,
      });
    }
  };
  
  const determineTrackForEffect = (effect: string): number => {
    switch (effect) {
      case "cut":
      case "speed":
        return 0; // Video track
      case "textOverlay":
      case "caption":
        return 1; // Text track
      case "fade":
        return 3; // Effects track
      case "colorGrade":
      case "brightness":
        return 4; // Format track
      default:
        return 2; // Other track
    }
  };

  return {
    handleChatCommand
  };
};
