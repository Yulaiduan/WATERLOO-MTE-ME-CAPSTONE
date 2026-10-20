// Encode numbered 1080p PNGs to a compact H.264 MP4 and decode verification frames.
// Usage: encoder FRAMES OUTPUT.mp4; 60 fps, 3 Mbit/s target, variable duration.
import Foundation
import AVFoundation
import AppKit
import CoreVideo

let directory = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
precondition(files.count > 0)
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
writer.shouldOptimizeForNetworkUse = true
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: 1920, AVVideoHeightKey: 1080,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 3000000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input,
    sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
        kCVPixelBufferWidthKey as String: 1920, kCVPixelBufferHeightKey as String: 1080,
        kCVPixelBufferCGImageCompatibilityKey as String: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey as String: true])
writer.add(input)
guard writer.startWriting() else { fatalError("Cannot start writer: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)
for (index, file) in files.enumerated() {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.005) }
    autoreleasepool {
        guard let image = NSImage(contentsOf: file)?.cgImage(forProposedRect: nil, context: nil, hints: nil)
        else { fatalError("Cannot read \(file)") }
        var buffer: CVPixelBuffer?
        guard CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &buffer) == kCVReturnSuccess,
              let pixel = buffer else { fatalError("Cannot allocate pixel buffer") }
        CVPixelBufferLockBaseAddress(pixel, [])
        let context = CGContext(data: CVPixelBufferGetBaseAddress(pixel), width: 1920, height: 1080,
            bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pixel),
            space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
        context.draw(image, in: CGRect(x: 0, y: 0, width: 1920, height: 1080))
        CVPixelBufferUnlockBaseAddress(pixel, [])
        guard adaptor.append(pixel, withPresentationTime: CMTime(value: Int64(index), timescale: 60))
        else { fatalError("Cannot append: \(String(describing: writer.error))") }
    }
}
input.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError("Encoding failed: \(String(describing: writer.error))") }
let asset = AVURLAsset(url: output)
let duration = CMTimeGetSeconds(asset.duration)
let track = asset.tracks(withMediaType: .video).first!
precondition(abs(duration - Double(files.count)/60) < 0.01)
precondition(track.naturalSize.width == 1920 && track.naturalSize.height == 1080)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
let verificationFrames = [30, 60, files.count/2, files.count-2].filter { $0 >= 0 && $0 < files.count }
for frame in verificationFrames {
    let image = try generator.copyCGImage(at: CMTime(value: Int64(frame), timescale: 60), actualTime: nil)
    let bitmap = NSBitmapImageRep(cgImage: image)
    try bitmap.representation(using: .png, properties: [:])!.write(to: output.deletingLastPathComponent().appendingPathComponent("decoded-frame-\(frame).png"))
}
let bytes = try FileManager.default.attributesOfItem(atPath: output.path)[.size] as! Int
let result: [String: Any] = ["passed": true, "frames": files.count, "duration_s": duration,
    "width": 1920, "height": 1080, "fps": track.nominalFrameRate,
    "codec": "H.264", "audio": false, "size_bytes": bytes, "decoded_frames": verificationFrames]
let json = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
try json.write(to: output.deletingLastPathComponent().appendingPathComponent("video-checks.json"))
print(String(data: json, encoding: .utf8)!)
