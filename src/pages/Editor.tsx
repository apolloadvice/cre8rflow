
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import NavBar from "@/components/NavBar";
import AssetPanel from "@/components/editor/AssetPanel";
import VideoPlayer from "@/components/editor/VideoPlayer";
import Timeline from "@/components/editor/Timeline";
import ChatPanel from "@/components/editor/ChatPanel";
import { Button } from "@/components/ui/button";
import { Save, FilmReel } from "lucide-react";

// Sample video URL for demo purposes
const SAMPLE_VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

interface Clip {
  id: string;
  start: number;
  end: number;
  track: number;
}

const Editor = () => {
  const { toast } = useToast();
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [videoSrc, setVideoSrc] = useState<string | undefined>(undefined);
  const [clips, setClips] = useState<Clip[]>([]);

  useEffect(() => {
    // Set the sample video after a short delay to simulate loading
    const timer = setTimeout(() => {
      setVideoSrc(SAMPLE_VIDEO_URL);
      toast({
        title: "Video loaded",
        description: "Sample video loaded successfully",
      });
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [toast]);

  const handleChatCommand = (command: string) => {
    console.log("Processing command:", command);
    
    // Simulate processing the command and adding clips to the timeline
    setTimeout(() => {
      // Generate some random clips based on the command
      const newClips: Clip[] = [];
      
      // Create 3-5 random clips
      const clipCount = Math.floor(Math.random() * 3) + 3;
      for (let i = 0; i < clipCount; i++) {
        const trackIndex = Math.floor(Math.random() * 3); // Random track 0-2
        const start = Math.random() * (duration * 0.8); // Random start time
        const clipDuration = Math.random() * 10 + 5; // 5-15 seconds
        const end = Math.min(start + clipDuration, duration);
        
        newClips.push({
          id: `clip-${Date.now()}-${i}`,
          start,
          end,
          track: trackIndex,
        });
      }
      
      setClips((prevClips) => [...prevClips, ...newClips]);
      
      toast({
        title: "Command processed",
        description: `Added ${newClips.length} new segments to the timeline`,
      });
    }, 2000);
  };

  const handleSaveProject = () => {
    toast({
      title: "Project saved",
      description: "Your project has been saved successfully",
    });
  };

  const handleRenderVideo = () => {
    toast({
      title: "Rendering started",
      description: "Your video is now being rendered",
    });
  };

  return (
    <div className="flex flex-col h-screen bg-cre8r-dark text-white">
      <NavBar />
      
      <div className="flex justify-between items-center px-4 h-14 border-b border-cre8r-gray-700 bg-cre8r-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-cre8r-violet rounded-full flex items-center justify-center">
            <FilmReel className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold">Untitled Project</h1>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            className="border-cre8r-gray-600 hover:border-cre8r-violet"
            onClick={handleSaveProject}
          >
            <Save className="h-4 w-4 mr-2" />
            Save Project
          </Button>
          
          <Button
            className="bg-cre8r-violet hover:bg-cre8r-violet-dark"
            onClick={handleRenderVideo}
          >
            Render Video
          </Button>
        </div>
      </div>
      
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Asset browser */}
        <div className="w-1/5 min-w-[240px] hidden md:block">
          <AssetPanel />
        </div>
        
        {/* Center panel - Video player and timeline */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 min-h-0">
            <VideoPlayer
              src={videoSrc}
              currentTime={currentTime}
              onTimeUpdate={setCurrentTime}
              onDurationChange={setDuration}
              className="h-full"
            />
          </div>
          <div className="h-64">
            <Timeline
              duration={duration}
              currentTime={currentTime}
              onTimeUpdate={setCurrentTime}
              clips={clips}
            />
          </div>
        </div>
        
        {/* Right panel - Chat interface */}
        <div className="w-1/5 min-w-[280px] hidden md:block">
          <ChatPanel onChatCommand={handleChatCommand} />
        </div>
      </div>
    </div>
  );
};

export default Editor;
