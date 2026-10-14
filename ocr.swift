import Vision
import AppKit
import Foundation

// Usage: swift ocr.swift <image.png>  -> prints recognized lines in reading order (top to bottom, left to right)
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = true
try VNImageRequestHandler(cgImage: cg).perform([req])
let obs = (req.results ?? []).sorted {
    let dy = $0.boundingBox.midY - $1.boundingBox.midY
    return abs(dy) > 0.01 ? dy > 0 : $0.boundingBox.minX < $1.boundingBox.minX
}
for o in obs { if let t = o.topCandidates(1).first { print(String(format: "%.2f\t%@", t.confidence, t.string)) } }
