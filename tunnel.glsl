vec3 check(vec2 p, float s)
{
	return  vec3(clamp(ceil(sin(p.x/s)*sin(p.y/s))*s * 10., 0.1, 1.0));
}

void main( void ) {
	
	float speed = touch.x * 2.0;
	vec2 position = ( gl_FragCoord.xy / resolution.xy ) + vec2(touch.x, touch.y) - 1.0;
	vec3 col = vec3(1.0);
	vec2 uv;
	vec2 p = position * 2.0;
	
	p *= vec2( resolution.x/resolution.y, 1.0 );
	p = vec2(cos(speed) * p.x + sin(speed) * p.y, -sin(speed) * p.x + cos(speed) *p.y);
	
	float y = length(p);

	uv.x = p.x/y;
	uv.y = 1.0 / abs(y) + time * 1.5;
	col = check(uv, .10);
	float t = pow(abs(y), 1.6);

	gl_FragColor = vec4( col*t, 1.0 );
}