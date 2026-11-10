#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <dlfcn.h>
#include <libretro.h>
static struct retro_keyboard_callback keyboard;
static const char *dir; static unsigned fmt, frames, audio_frames; static uint64_t hash; static unsigned width,height; static unsigned char *pixels;
static struct { char *key,*value; } opts[512]; static unsigned nopts;
static void logger(enum retro_log_level level,const char *format,...) { va_list ap; va_start(ap,format); vfprintf(stderr,format,ap); va_end(ap); }
static bool env(unsigned cmd,void *data){switch(cmd){
case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY: case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: case RETRO_ENVIRONMENT_GET_CONTENT_DIRECTORY: *(const char**)data=dir;return true;
case RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK: keyboard=*(struct retro_keyboard_callback*)data;return true;
case RETRO_ENVIRONMENT_GET_CAN_DUPE: *(bool*)data=true;return true;
case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: fmt=*(unsigned*)data;return true;
case RETRO_ENVIRONMENT_GET_LOG_INTERFACE: ((struct retro_log_callback*)data)->log=logger;return true;
case RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION: *(unsigned*)data=0;return true;
case RETRO_ENVIRONMENT_SET_VARIABLES: {const struct retro_variable *v=data;for(;v->key&&nopts<512;v++){opts[nopts].key=strdup(v->key);const char *p=strchr(v->value,';');p=p?p+2:v->value;opts[nopts].value=strdup(p);char *q=strchr(opts[nopts].value,'|');if(q)*q=0;nopts++;}return true;}
case RETRO_ENVIRONMENT_GET_VARIABLE: {struct retro_variable *v=data;if(!strcmp(v->key,"fceumm_region")){v->value="PAL";return true;}if(!strncmp(v->key,"fceumm_overscan_",16)){v->value="0";return true;}if(!strcmp(v->key,"puae_model") && getenv("PUAE_MODEL")){v->value=getenv("PUAE_MODEL");return true;}for(unsigned i=0;i<nopts;i++)if(!strcmp(v->key,opts[i].key)){v->value=opts[i].value;return true;}v->value=NULL;return false;}
case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE: *(bool*)data=false;return true;
case RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME: case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS: case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO: case RETRO_ENVIRONMENT_SET_GEOMETRY: case RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO: return true;
case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS: return true;
case RETRO_ENVIRONMENT_GET_LANGUAGE: *(unsigned*)data=RETRO_LANGUAGE_ENGLISH;return true;
default:return false;}}
static void video(const void*d,unsigned w,unsigned h,size_t pitch){frames++;if(!d)return;width=w;height=h;pixels=realloc(pixels,w*h*3);hash=1469598103934665603ULL;for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){uint32_t v;unsigned r,g,b;if(fmt==RETRO_PIXEL_FORMAT_XRGB8888){v=((const uint32_t*)((const char*)d+y*pitch))[x];r=(v>>16)&255;g=(v>>8)&255;b=v&255;}else{v=((const uint16_t*)((const char*)d+y*pitch))[x];if(fmt==RETRO_PIXEL_FORMAT_RGB565){r=((v>>11)&31)*255/31;g=((v>>5)&63)*255/63;}else{r=((v>>10)&31)*255/31;g=((v>>5)&31)*255/31;}b=(v&31)*255/31;}unsigned off=(y*w+x)*3;pixels[off]=r;pixels[off+1]=g;pixels[off+2]=b;hash=(hash^v)*1099511628211ULL;}}
static void sample(int16_t l,int16_t r){audio_frames++;}static size_t batch(const int16_t*d,size_t n){audio_frames+=n;return n;}static unsigned input_frame;
static void poll(void){input_frame++;}
static int16_t input(unsigned p,unsigned d,unsigned i,unsigned id){
 if(p>1||d!=RETRO_DEVICE_JOYPAD)return 0;
 unsigned mask=0;
 if(!p){
 if(getenv("NES_SCRIPT_INPUT")&&((input_frame>=1200&&input_frame<1203)||(input_frame>=1600&&input_frame<1603)||(input_frame>=2000&&input_frame<2003)||(input_frame>=2400&&input_frame<2403)))mask=1u<<RETRO_DEVICE_ID_JOYPAD_START;
 if(getenv("NES_PORT_MENU")){
  if(input_frame>=1200&&input_frame<1205)mask=1u<<RETRO_DEVICE_ID_JOYPAD_START;
  if(input_frame>=1500&&input_frame<1505)mask=1u<<RETRO_DEVICE_ID_JOYPAD_DOWN;
  if((input_frame>=1700&&input_frame<1705)||(input_frame>=1900&&input_frame<1905))mask=1u<<RETRO_DEVICE_ID_JOYPAD_A;
 }
 if(getenv("AMIGA_MENU_INPUT")){
  if(input_frame>=1500&&input_frame<1505)mask=1u<<(getenv("AMIGA_MENU_UP")?RETRO_DEVICE_ID_JOYPAD_UP:RETRO_DEVICE_ID_JOYPAD_DOWN);
  if(getenv("AMIGA_MENU_CONFIRM")&&input_frame>=1700&&input_frame<1705)mask=1u<<RETRO_DEVICE_ID_JOYPAD_B;
  if(getenv("AMIGA_MENU_CANCEL")&&input_frame>=1850&&input_frame<1855)mask=1u<<RETRO_DEVICE_ID_JOYPAD_A;
  if(getenv("AMIGA_MENU_COMMIT")&&input_frame>=1900&&input_frame<1905)mask=1u<<RETRO_DEVICE_ID_JOYPAD_B;
 }
 }
 /* Optional deterministic events: first:last:libretro-mask, comma separated.
    Existing regression input modes remain unchanged when unset. */
 const char *events=getenv(p?"PORT2_INPUT_EVENTS":"PORT_INPUT_EVENTS");
 if(events){
  const char *q=events;
  while(*q){char *end;unsigned first=strtoul(q,&end,0);if(*end!=':')break;q=end+1;
   unsigned last=strtoul(q,&end,0);if(*end!=':')break;q=end+1;
   unsigned event_mask=strtoul(q,&end,0);
   if(input_frame>=first&&input_frame<last)mask|=event_mask;
   if(*end!=',')break;q=end+1;
  }
 }
 if(id==RETRO_DEVICE_ID_JOYPAD_MASK)return mask;
 return id<16?!!(mask&(1u<<id)):0;
}
#define FN(ret,name,args) ret (*name)args=dlsym(lib,#name)
int main(int argc,char**argv){if(argc<5)return 2;void*lib=dlopen(argv[1],RTLD_NOW);if(!lib){puts(dlerror());return 2;}dir=argv[3];FN(void,retro_set_environment,(retro_environment_t));FN(void,retro_set_video_refresh,(retro_video_refresh_t));FN(void,retro_set_audio_sample,(retro_audio_sample_t));FN(void,retro_set_audio_sample_batch,(retro_audio_sample_batch_t));FN(void,retro_set_input_poll,(retro_input_poll_t));FN(void,retro_set_input_state,(retro_input_state_t));FN(void,retro_init,(void));FN(void,retro_set_controller_port_device,(unsigned,unsigned));FN(bool,retro_load_game,(const struct retro_game_info*));FN(void,retro_run,(void));FN(void,retro_get_system_av_info,(struct retro_system_av_info*));FN(unsigned,retro_get_region,(void));FN(void,retro_unload_game,(void));FN(void,retro_deinit,(void));FN(void,retro_get_system_info,(struct retro_system_info*));FN(void*,retro_get_memory_data,(unsigned));FN(size_t,retro_get_memory_size,(unsigned));
retro_set_environment(env);retro_set_video_refresh(video);retro_set_audio_sample(sample);retro_set_audio_sample_batch(batch);retro_set_input_poll(poll);retro_set_input_state(input);retro_init();if(retro_set_controller_port_device){retro_set_controller_port_device(0,RETRO_DEVICE_JOYPAD);retro_set_controller_port_device(1,RETRO_DEVICE_JOYPAD);}struct retro_system_info si;retro_get_system_info(&si);printf("core=%s version=%s\n",si.library_name,si.library_version);struct retro_game_info game={0};struct retro_game_info *gp=NULL;if(strcmp(argv[2],"--no-content")){game.path=argv[2];if(!si.need_fullpath){FILE*f=fopen(argv[2],"rb");if(!f)return 3;fseek(f,0,SEEK_END);game.size=ftell(f);rewind(f);void*buf=malloc(game.size);fread(buf,1,game.size,f);fclose(f);game.data=buf;}gp=&game;}if(!retro_load_game(gp)){fprintf(stderr,"load failed\n");return 4;}struct retro_system_av_info av;retro_get_system_av_info(&av);printf("region=%u fps=%.9f sample_rate=%.3f\n",retro_get_region(),av.timing.fps,av.timing.sample_rate);unsigned count=atoi(argv[4]);for(unsigned i=0;i<count;i++){
 if(getenv("RAM_LOAD")&&getenv("RAM_LOAD_FRAME")&&i==(unsigned)strtoul(getenv("RAM_LOAD_FRAME"),NULL,0)){
  size_t sz=retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);void *dst=retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);
  FILE *fixture=fopen(getenv("RAM_LOAD"),"rb");if(!fixture||!dst||!sz){fprintf(stderr,"RAM fixture unavailable\n");return 6;}
  fseek(fixture,0,SEEK_END);long bytes=ftell(fixture);rewind(fixture);if(bytes!=(long)sz||fread(dst,1,sz,fixture)!=sz){fprintf(stderr,"RAM fixture size mismatch\n");return 7;}fclose(fixture);
 }
 const char *keys=getenv("KEY_INPUT_EVENTS");
 if(keys&&keyboard.callback){const char *q=keys;while(*q){char *end;unsigned first=strtoul(q,&end,0);if(*end!=':')break;q=end+1;unsigned last=strtoul(q,&end,0);if(*end!=':')break;q=end+1;unsigned key=strtoul(q,&end,0);if(i==first)keyboard.callback(true,key,0,0);if(i==last)keyboard.callback(false,key,0,0);if(*end!=',')break;q=end+1;}}
 retro_run();
}printf("PASS runs=%u video_callbacks=%u dimensions=%ux%u audio_frames=%u frame_hash=%016llx\n",count,frames,width,height,audio_frames,(unsigned long long)hash);size_t m=retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM);uint8_t*ram=retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM);if(ram&&m)printf("system_ram=%zu first_byte=%u\n",m,ram[0]);if(argc>5&&pixels){FILE*f=fopen(argv[5],"wb");fprintf(f,"P6\n%u %u\n255\n",width,height);fwrite(pixels,3,width*height,f);fclose(f);}if(ram&&m&&getenv("RAM_OUT")){FILE*f=fopen(getenv("RAM_OUT"),"wb");if(f){fwrite(ram,1,m,f);fclose(f);}}retro_unload_game();retro_deinit();return frames?0:5;}
