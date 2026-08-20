from opentube.domain.models import AudioFormatOption, MediaMetadata, VideoFormatOption


class FormatSelectionService:
    @staticmethod
    def get_video_options(metadata: MediaMetadata) -> list[VideoFormatOption]:
        options_map = {}
        for fmt in metadata.formats:
            if fmt.is_audio_only:
                continue
                
            # We want to group by resolution (like "1080p")
            res_str = fmt.quality
            if "p" not in res_str:
                if res_str.isdigit():
                    res_str = f"{res_str}p"
                else:
                    res_str = "Unknown"
                    
            if res_str == "unknown" or res_str == "Unknown":
                continue

            # In a real app we'd rank them better, but we take the first seen for simplicity
            if res_str not in options_map:
                options_map[res_str] = VideoFormatOption(
                    format_id=fmt.format_id, # Might be a single stream or combo
                    resolution=res_str,
                    fps=fmt.fps,
                    video_codec=fmt.vcodec,
                    audio_codec=fmt.acodec,
                    filesize_approx=fmt.filesize
                )
                
        # Sort descending by resolution (assuming numeric part)
        def sort_key(opt: VideoFormatOption) -> int:
            num = ''.join(filter(str.isdigit, opt.resolution))
            return int(num) if num else 0
            
        return sorted(options_map.values(), key=sort_key, reverse=True)

    @staticmethod
    def get_audio_options(metadata: MediaMetadata) -> list[AudioFormatOption]:
        # Find the max source audio bitrate to bound our output choices
        max_abr = 0.0
        for fmt in metadata.formats:
            if fmt.abr and fmt.abr > max_abr:
                max_abr = fmt.abr
            elif fmt.is_audio_only and fmt.tbr and fmt.tbr > max_abr:
                max_abr = fmt.tbr
                
        # If no explicit bitrate found, fallback to 160 as safe assumption for most YT streams
        if max_abr <= 0:
            max_abr = 160.0
            
        # Standard MP3 target bitrates
        standard_bitrates = [320, 256, 192, 160, 128]
        
        options = []
        best_audio_format_id = "bestaudio/best" # Let yt-dlp pick the best source automatically
        
        for br in standard_bitrates:
            # We allow up to slightly above max_abr because sometimes 130abr is presented as 128 or 160
            if max_abr * 1.2 >= br or br == 128: 
                # Provide a rough file size estimate (bitrate * duration)
                # filesize = (kbps * 1000 * seconds) / 8
                approx_size = None
                if metadata.duration:
                    approx_size = int((br * 1000 * metadata.duration) / 8)
                    
                options.append(AudioFormatOption(
                    format_id=best_audio_format_id,
                    bitrate_kbps=br,
                    filesize_approx=approx_size
                ))
                
        return options
