import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import NavBar from "@/components/NavBar";
import AssetPanel from "@/components/editor/AssetPanel";
import VideoPlayer from "@/components/editor/VideoPlayer";
import Timeline from "@/components/editor/Timeline";
import ChatPanel from "@/components/editor/ChatPanel";
import { Button } from "@/components/ui/button";
import { Save, Film } from "lucide-react";

const SAMPLE_VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

interface Clip {
  id: string;
  start: number;
  end: number;
  track: number;
  type: string;
  name: string;
}

interface VideoAsset {
  id: string;
  name: string;
  thumbnail: string;
  duration: number;
  uploaded: Date;
  src?: string;
}

const Editor = () => {
  const { toast } = useToast();
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [videoSrc, setVideoSrc] = useState<string | undefined>(undefined);
  const [clips, setClips] = useState<Clip[]>([]);
  const [activeVideoAsset, setActiveVideoAsset] = useState<VideoAsset | null>(null);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);

  useEffect(() => {
    if (!activeVideoAsset) {
      const timer = setTimeout(() => {
        setVideoSrc(SAMPLE_VIDEO_URL);
        toast({
          title: "Video loaded",
          description: "Sample video loaded successfully",
        });
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [toast, activeVideoAsset]);

  const handleVideoSelect = (video: VideoAsset) => {
    setClips([]);
    setActiveVideoAsset(video);
    
    if (video.src) {
      setVideoSrc(video.src);
    } else if (video.id === "1") {
      setVideoSrc(SAMPLE_VIDEO_URL);
    }
    
    toast({
      title: "Video selected",
      description: `${video.name} is now ready to edit`,
    });
  };

  const handleVideoDrop = (file: File, track: number, dropTime: number) => {
    const videoUrl = URL.createObjectURL(file);
    
    const video = document.createElement("video");
    video.src = videoUrl;
    
    video.onloadedmetadata = () => {
      const clipDuration = video.duration;
      const newClip: Clip = {
        id: `clip-${Date.now()}`,
        start: dropTime,
        end: dropTime + clipDuration,
        track,
        type: "video",
        name: file.name
      };
      
      setClips(prevClips => [...prevClips, newClip]);
      setSelectedClipId(newClip.id);
      
      if (!videoSrc) {
        setVideoSrc(videoUrl);
        setDuration(clipDuration);
      }
      
      toast({
        title: "Video added to timeline",
        description: `${file.name} has been added to track ${track + 1}`,
      });
    };
  };

  const handleChatCommand = (command: string) => {
    if (!selectedClipId) {
      toast({
        title: "No clip selected",
        description: "Please select a clip on the timeline first",
        variant: "destructive",
      });
      return;
    }
    
    console.log("Processing command:", command);
    
    const lowerCommand = command.toLowerCase();
    
    const selectedClip = clips.find(clip => clip.id === selectedClipId);
    if (!selectedClip) return;
    
    toast({
      title: "Processing command",
      description: "Analyzing your edit request...",
    });
    
    setTimeout(() => {
      const updatedClips = clips.map(clip => {
        if (clip.id !== selectedClipId) return clip;
        
        let type = clip.type;
        let name = clip.name;
        
        if (lowerCommand.includes("trim") || lowerCommand.includes("cut")) {
          type = "trim";
          name = "Trimmed " + (clip.name || "");
        } 
        else if (lowerCommand.includes("highlight")) {
          type = "highlight";
          name = "Highlighted " + (clip.name || "");
        }
        else if (lowerCommand.includes("subtitle") || lowerCommand.includes("caption")) {
          type = "subtitle";
          name = "Subtitled " + (clip.name || "");
        }
        else if (lowerCommand.includes("music") || lowerCommand.includes("audio")) {
          type = "audio";
          name = "Audio Added " + (clip.name || "");
        }
        else if (lowerCommand.includes("color") || lowerCommand.includes("grade")) {
          type = "color";
          name = "Color Graded " + (clip.name || "");
        }
        else if (lowerCommand.includes("crop") || lowerCommand.includes("vertical")) {
          type = "crop";
          name = "Cropped " + (clip.name || "");
        }
        
        return { ...clip, type, name };
      });
      
      setClips(updatedClips);
      
      toast({
        title: "Edit applied",
        description: `Applied ${lowerCommand} to the selected clip`,
      });
    }, 1500);
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
            <Film className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold">
            {activeVideoAsset ? `Editing: ${activeVideoAsset.name}` : "Untitled Project"}
          </h1>
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
        <div className="w-1/5 min-w-[240px] hidden md:block">
          <AssetPanel onVideoSelect={handleVideoSelect} />
        </div>
        
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
              onClipSelect={setSelectedClipId}
              selectedClipId={selectedClipId}
              onVideoDrop={handleVideoDrop}
            />
          </div>
        </div>
        
        <div className="w-1/5 min-w-[280px] hidden md:block">
          <ChatPanel onChatCommand={handleChatCommand} />
        </div>
      </div>
    </div>
  );
};

export default Editor;
