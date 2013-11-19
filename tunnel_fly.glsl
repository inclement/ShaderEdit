// Original from https://www.shadertoy.com/view/4dfGzf
// srtuss, 2013
// raymarching a scifi tech tunnel textured with voronoi noise

// added blend effect

#define PI 3.14159265358979323

vec2 rotate(vec2 p, float a)
{
        return vec2(p.x * cos(a) - p.y * sin(a), p.x * sin(a) + p.y * cos(a));
}

// iq's fast 3d noise
float noise3d(in vec3 x)
{
    vec3 p = floor(x);
    vec3 f = fract(x);
        f = f * f * (3.0 - 2.0 * f);
        vec2 uv = (p.xy + vec2(37.0, 17.0) * p.z) + f.xy;
        vec2 rg = vec2(0.3,0.6); //texture2D(iChannel0, (uv + 0.5) / 256.0, -100.0).yx;
        return mix(rg.x, rg.y, f.z);
}

// 3d fbm
float fbm3(vec3 p)
{
        return noise3d(p) * 0.5 + noise3d(p * 2.02) * 0.25 + noise3d(p * 4.01) * 0.125;
}

// i'm currently trying something here:
float hash(float x)
{
        return fract(484.982 * sin(x)) * 2.0 - 1.0;
}
float noise(float x)
{
        float fl = floor(x);
        return mix(hash(fl), hash(fl + 1.0), smoothstep(0.0, 1.0, fract(x)));
}
float fbm(float x)
{
        return noise(x) * 0.5 + noise(x * 2.2) * 0.1 + noise(x * 4.1) * 0.005;
}
float stepnoise(float x)
{
        float fl = floor(x);
        return mix(hash(fl), hash(fl + 1.0), pow(fract(x), 0.3));
}
float mechnoise(float x)
{
        float fl = floor(x);
        return mix(hash(fl), hash(fl + 1.0), clamp(fract(x) * 2.0, 0.0, 1.0));
}

float vTime;


// animated 3d fbm
float fbm3a(vec3 p)
{
        vec2 t = vec2(vTime * 0.4, 0.0);
        return noise3d(p + t.xyy) * 0.5 + noise3d(p * 2.02 - t.xyy) * 0.25 + noise3d(p * 4.01 + t.yxy) * 0.125;
}

// more animated 3d fbm
float fbm3a_(vec3 p)
{
        vec2 t = vec2(vTime * 0.4, 0.0);
        return noise3d(p + t.xyy) * 0.5 + noise3d(p * 2.02 - t.xyy) * 0.25 + noise3d(p * 4.01 + t.yxy) * 0.125 + noise3d(p * 8.03 + t.yxy) * 0.0625;
}


vec2 rand2(in vec2 p)
{
        return fract(vec2(sin(p.x * 591.32 + p.y * 154.077), cos(p.x * 391.32 + p.y * 49.077)));
}

// voronoi distance noise, based on iq's articles
float voronoi(in vec2 x)
{
        vec2 p = floor(x);
        vec2 f = fract(x);
        
        vec2 res = vec2(8.0);
        for(int j = -1; j <= 1; j ++)
        {
                for(int i = -1; i <= 1; i ++)
                {
                        vec2 b = vec2(i, j);
                        vec2 r = vec2(b) - f + rand2(p + b);
                        
                        // chebyshev distance, one of many ways to do this
                        float d = max(abs(r.x), abs(r.y));
                        
                        if(d < res.x)
                        {
                                res.y = res.x;
                                res.x = d;
                        }
                        else if(d < res.y)
                        {
                                res.y = d;
                        }
                }
        }
        return res.y - res.x;
}

// describes the tunnel path
vec2 path(float z)
{
        return vec2(sin(z * 0.1333) * 2.0, cos(z * 0.2) * 2.0);
}

// this creates cool rectangular detail on a given distance field
void technify(vec3 p, inout float d1)
{
        d1 *= 0.3;
        p *= 0.3;

        vec4 h = vec4(0.0);
        
        float p1 = 0.06;
        float p2 = 0.0;
        
        // inspired from cdak source code
        for(float i = 0.0; i < 4.0; i ++)
        {
                vec3 pp = p;
                vec3 q = 1.0 + i * i * 0.18 * (1.0 + 4.0 * (1.0 + 0.3 * p2) * sin(vec3(5.7, 6.4, 7.3) * i * 1.145 + 0.3 * sin(h.w * 0.015) * (3.0 + i)));
                vec3 g = (fract(pp * q) - 0.5) / q;
                
                d1 = min(d1 + 0.03 + p1, max(d1, max(abs(g.x), max(abs(g.y), abs(g.z))) - 0.148));
        }
        
        d1 = d1 / 0.28;
}

float scene(vec3 p)
{
        float t = vTime * 1.0;
        
        float v, w;
        
        p.xy += path(p.z);
        p.xy = rotate(p.xy, t * 1.0);
        
        float s = sin(p.z * 0.4 + time * 0.0) * 0.5;
        
        float l = length(p.xy) + s;
        
        v = max(3.0 - l, l - 5.0);
        
        //technify(p, v);
        
        return v;
}

vec3 normal(vec3 p)
{
        float c = scene(p);
        vec2 h = vec2(0.01, 0.0);
        vec3 nml;
        nml.x = scene(p + h.xyy) - c;
        nml.y = scene(p + h.yxy) - c;
        nml.z = scene(p + h.yyx) - c;
        return normalize(nml);
}

// background
vec3 sky(vec3 p)
{
        vec3 col;
        float v = 1.0 - abs(fbm3a(p * 4.0) * 2.0 - 1.0);
        float n = fbm3a_(p * 7.0 - 104.042);
        v = mix(v, pow(n, 0.3), 0.5);
        
        col = vec3(pow(vec3(v), vec3(13.0, 7.0, 6.0))) * 0.8;
        return col;
}

vec3 shade(vec3 p, vec3 dir, vec3 nml, vec3 ref, float dist)
{
        vec3 col;
        
        // cheap diffuse and specular light
        vec3 sun = normalize(vec3(0.2, 1.0, 0.3));
        float diff = dot(nml, sun) * 0.5 + 0.5;
        float spec = max(dot(ref, sun), 0.0);
        spec = pow(spec, 32.0);
        col = vec3(0.25, 0.4, 0.5) * diff + spec;
        
        // a little more detail using voronoi noise as a radial texture
        vec3 q = p;
        q.xy += path(p.z);
        float a = atan(q.x, q.y) - vTime;
        float l = q.z * 1.0 + 0.0 * length(q.xy);
        
        float li = smoothstep(0.4, 1.0, sin(p.z * 0.2 + vTime * 5.0));
        float vo = smoothstep(0.90, 1.0, 1.0 - voronoi(1.5 * vec2(a * 3.0, l)));
        
        col = mix(mix(col, vec3(0.5, 0.8, 1.0) * 0.2, vo), col + vec3(vo) * 0.6, li);
        
        // sky reflections
        col = mix(col, sky(ref), 0.3);
        
        return col;
}

void main(void)
{
        vTime = time * 1.0 + 1.0;
        // playing with vTime
        float seg = 10.0;
        float tfl = floor(vTime / seg) * seg;
        float tfr = mod(vTime, seg);
        vTime = tfl + tfr - pow(clamp(tfr - 8.0, 0.0, 1.0), 4.0) * (tfr - 9.0) * 0.99 + sin(vTime * 20.0) * pow(2.0 * clamp(tfr - 9.5, 0.0, 1.0), 2.0);
        
        vec2 uv = gl_FragCoord.xy / resolution.xy;
        uv = uv * 2.0 - 1.0;
        uv.x *= resolution.x / resolution.y;
        
        float t = vTime;
        
        vec3 eye = vec3(0.0, 0.0, t * 15.0);
        vec3 dir = normalize(vec3(uv, 1.1));
        
        
        // 3 different camera setups
        
        float ct = mod(t * 0.2, 3.0);
        float blend = smoothstep(0.98, 1.0, cos(PI * 2.0 * t * 0.2));
        if(ct > 2.0)
        {
                eye.y += 20.0;
                dir.yz = rotate(dir.yz, sin(t) * 0.2 + PI * 0.5);
                dir.xz = rotate(dir.xz, cos(t) * 0.5);
        }
        else if(ct > 1.0)
        {
                eye.xy -= path(eye.z);
                eye.y += 0.0;
                dir.yz = rotate(dir.yz, sin(t) * 0.5 + 0.5);
                dir.xz = rotate(dir.xz, cos(t) * 0.5);
        }
        else
        {
                eye.xy -= path(eye.z);
                eye.y += 8.0;
                dir.yz = rotate(dir.yz, sin(t * 1.77) * 0.2);
                dir.xz = rotate(dir.xz, cos(t * 1.77) * 0.2);
        }
        
        
        vec3 col = sky(dir);
        
        // raymarch
        float d = 0.0;
        vec3 ray = eye;
        for(int i = 0; i < 100; i ++)
        {
                d += scene(eye + dir * d) * 0.7;
        }
        ray = eye + dir * d;
        
        // without these two lines there is a bug that i don't know how to fix
        d = distance(eye, ray);
        d = clamp(d, 0.0, 100.0);
        
        if(d < 100.0)
        {
                vec3 nml = normal(ray);
                col = shade(ray, dir, nml, reflect(dir, nml), d);
        }
        
        // dramatize colors
        col = pow(col, vec3(1.5)) * 2.0;
        
        // vignetting
        vec2 q = gl_FragCoord.xy / resolution.xy;
        col *= 0.2 + 0.8 * pow(16.0 * q.x * q.y * (1.0 - q.x) * (1.0 - q.y), 0.1);

        // blend
        col = mix(col, vec3(1.0), blend);
        
        gl_FragColor = vec4(col, 1.0);
}
