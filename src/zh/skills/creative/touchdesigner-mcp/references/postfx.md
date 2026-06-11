# 后处理特效参考

适用于实时视觉创作的光晕效果、CRT扫描线、色差以及反馈辉光图案。

---

## 光晕效果

### 内置光晕效果 TOP

TD的`bloomTOP`是效率最高的方案——依托GPU加速，无需编写着色器即可实现。

```python
bloom = root.create(bloomTOP, 'bloom1')
bloom.par.threshold = 0.6     # Luminance threshold (0-1)
bloom.par.size = 0.03         # Spread radius (0-1)
bloom.par.strength = 1.5      # Bloom intensity
bloom.par.blendmode = 'add'   # 'add' or 'screen'
```

**音频响应光晕效果：**
```python
bloom.par.strength.mode = ParMode.EXPRESSION
bloom.par.strength.expr = "op('audio_env')['envelope'][0] * 3.0 + 0.5"
```

### GLSL光晕效果（更高控制度）

适用于带颜色色调的多通道光晕效果：

```glsl
// bloom_pixel.glsl — pass1: threshold + tint
out vec4 fragColor;
uniform float uThreshold;
uniform vec3 uBloomColor;

void main() {
    vec4 col = texture(sTD2DInputs[0], vUV.st);
    float luma = dot(col.rgb, vec3(0.299, 0.587, 0.114));
    float bloom = max(0.0, luma - uThreshold);
    fragColor = TDOutputSwizzle(vec4(col.rgb * bloom * uBloomColor, col.a));
}
```

随后使用 `blurTOP`（大小约为 0.02-0.05）进行模糊处理，再通过“添加”模式下的 `addTOP` 或 `compositeTOP` 将处理后的图像叠加回原始图像上。

```glsl
// crt_pixel.glsl
out vec4 fragColor;
uniform float uTime;
uniform float uScanlineIntensity;  // 0.0 - 1.0, default 0.4
uniform float uCurvature;          // 0.0 - 0.15, default 0.05
uniform float uVignette;           // 0.0 - 1.0, default 0.8

vec2 curveUV(vec2 uv, float amount) {
    uv = uv * 2.0 - 1.0;
    vec2 offset = abs(uv.yx) / vec2(6.0, 4.0);
    uv = uv + uv * offset * offset * amount;
    return uv * 0.5 + 0.5;
}

void main() {
    vec2 res = uTDOutputInfo.res.zw;
    vec2 uv = vUV.st;

    // CRT barrel distortion
    uv = curveUV(uv, uCurvature * 10.0);

    // Kill pixels outside curved screen
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec4 col = texture(sTD2DInputs[0], uv);

    // Scanlines
    float scanline = sin(uv.y * res.y * 3.14159) * 0.5 + 0.5;
    col.rgb *= mix(1.0, scanline, uScanlineIntensity);

    // Horizontal noise flicker
    float flicker = TDSimplexNoise(vec2(uv.y * 100.0, uTime * 8.0)) * 0.03;
    col.rgb += flicker;

    // Vignette
    vec2 vig = uv * (1.0 - uv.yx);
    float v = pow(vig.x * vig.y * 15.0, uVignette);
    col.rgb *= v;

    fragColor = TDOutputSwizzle(col);
}
```

## 色差效果

该功能可分离RGB通道，并沿屏幕坐标轴对它们进行偏移处理。

```glsl
out vec4 fragColor;
uniform float uAmount;   // 0.001 - 0.02, default 0.006

void main() {
    vec2 uv = vUV.st;
    vec2 dir = uv - 0.5;

    float r = texture(sTD2DInputs[0], uv + dir * uAmount).r;
    float g = texture(sTD2DInputs[0], uv).g;
    float b = texture(sTD2DInputs[0], uv - dir * uAmount).b;
    float a = texture(sTD2DInputs[0], uv).a;

    fragColor = TDOutputSwizzle(vec4(r, g, b, a));
}
```

**音频响应版本**——节拍点处的脉冲异常现象：
```glsl
uniform float uBeat;
void main() {
    vec2 uv = vUV.st;
    vec2 dir = uv - 0.5;
    float amount = uAmount + uBeat * 0.04;
    float r = texture(sTD2DInputs[0], uv + dir * amount * 1.2).r;
    float g = texture(sTD2DInputs[0], uv).g;
    float b = texture(sTD2DInputs[0], uv - dir * amount * 0.8).b;
    fragColor = TDOutputSwizzle(vec4(r, g, b, 1.0));
}
```

## 反馈辉光效果

用于实现辉光效果的温暖持久尾迹。

```glsl
out vec4 fragColor;
uniform float uDecay;     // 0.92 - 0.98 for slow trails
uniform vec3 uGlowColor;  // tint accumulated feedback

void main() {
    vec2 uv = vUV.st;
    vec4 prev = texture(sTD2DInputs[0], uv);  // feedback input
    vec4 curr = texture(sTD2DInputs[1], uv);  // current frame

    vec3 glow = prev.rgb * uDecay * uGlowColor;
    vec3 result = max(glow, curr.rgb);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
```

**提示：**
- `uDecay = 0.95` → 中等长度的尾迹
- `uDecay = 0.98` → 长形的彗星尾迹
- 若需平滑的渐变效果，请将 `glslTOP` 的格式设置为 `rgba16float`

---

## 完整的后处理效果堆栈

推荐顺序：

```
[scene / composite]
        ↓
   bloomTOP          ← luminance threshold bloom
        ↓
   glslTOP (chrom)   ← chromatic aberration
        ↓
   glslTOP (crt)     ← scanlines + barrel distortion + vignette
        ↓
   null_out          ← final output
```

**性能说明：** 每个 glslTOP 对应一次完整的 GPU 处理流程。在 1920×1080 分辨率、60fps 的场景下，该技术栈可轻松实现实时渲染。而对于 4K 分辨率，则建议先使用 `resolutionTOP` 减小光晕效果的输入分辨率，以此提升性能。
