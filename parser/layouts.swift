import Carbon
import Foundation

func strProp(_ src: TISInputSource, _ key: CFString) -> String? {
guard let p = TISGetInputSourceProperty(src, key) else { return nil }
return Unmanaged<CFString>.fromOpaque(p).takeUnretainedValue() as String
}

let list = TISCreateInputSourceList(nil, true)!.takeRetainedValue() as!
[TISInputSource]
for src in list {
guard let type = strProp(src, kTISPropertyInputSourceType),
type == (kTISTypeKeyboardLayout as String),
let id = strProp(src, kTISPropertyInputSourceID),
id.hasPrefix("com.apple.") else { continue }
let name = strProp(src, kTISPropertyLocalizedName) ?? ""
print("\(id)\t\(name)")
}
