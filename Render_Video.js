const { CanvasRenderingContext2D, createCanvas, loadImage } = require("canvas");
const fs = require("fs");
const { LoadResources } = require("./res.js");
const pywebcanvas_api = require("./pywebcanvas_api.js");
const argv = process.argv.splice(2);

const lfdaot_fp = argv[0];
const audio_fp = argv[1];
const background_fp = argv[2];
const sound_name = argv[3];
const level = argv[4];
const output_fp = argv[5];

const lfdaot_object = JSON.parse(fs.readFileSync(lfdaot_fp));
const screen_size = lfdaot_object["meta"]["size"];
const screen_width = screen_size[0];
const screen_height = screen_size[1];
const fps = lfdaot_object["meta"]["frame_speed"];
const frame_num = lfdaot_object["meta"]["frame_num"];

CanvasRenderingContext2D.prototype.drawRotateImage = function(im,x,y,width,height,deg) { // draw at the position center
    if (!!deg){
        this.save();
        this.translate(x,y);
        this.rotate(deg * Math.PI / 180);
        this.drawImage(im,-width / 2,-height / 2,width,height);
        this.restore();
    }
    else {
        this.drawImage(im,x - width / 2,y - height / 2,width,height);
    }
}

CanvasRenderingContext2D.prototype.drawAnchorESRotateImage = function(im,x,y,width,height,deg) {
    if (!!deg){
        this.save();
        this.translate(x,y);
        this.rotate(deg * Math.PI / 180);
        this.drawImage(im,-width / 2,-height,width,height);
        this.restore();
    }
    else {
        this.drawImage(im,x - width / 2,y - height,width,height);
    }
}

var canvas = createCanvas(screen_width, screen_height);
var ctx = canvas.getContext("2d",{alpha:true});
const render_function_mapping = {
    clear_canvas:pywebcanvas_api.clear_canvas,
    draw_background:pywebcanvas_api.draw_background,
    draw_ui:pywebcanvas_api.draw_ui,
    create_line:pywebcanvas_api.create_line,
    create_text:pywebcanvas_api.create_text,
    create_image:pywebcanvas_api.create_image,
    create_rectangle:pywebcanvas_api.create_rectangle,
    run_js_wait_code:() => {},
    run_js_code:pywebcanvas_api.eval_api
}

function args_kwargs_parser(args,kwargs) {
    r_str = "";
    for (var arg of args) {
        if (typeof arg == "string") {
            r_str += `"${arg}",`;
        }
        else {
            r_str += `${arg.toString()},`;
        }
    }
    r_str += `${JSON.stringify(kwargs)}`;
    return r_str;
}

async function main(){
    res = await LoadResources();

    try {
        pywebcanvas_api.init(
            ctx,screen_width,screen_height,
            await loadImage(background_fp),sound_name,level,
            res,canvas
        );
    }
    catch (err) {
        console.log("Your background image file name cannot has chinese string.");
    }
    
    render_frame_count = 0;
    for (frame_data of lfdaot_object["data"]) {
        for (render_tasks of frame_data["render"]) {
            arg_string = args_kwargs_parser(render_tasks["args"],render_tasks["kwargs"]);
            eval(`render_function_mapping.${render_tasks["func_name"]}(${arg_string});`);
        }
        frame_buf = canvas.toBuffer();
        render_frame_count ++;
        fs.writeFileSync(`${output_fp}/${render_frame_count}.png`,frame_buf);
        console.log(`render frame ${render_frame_count}/${frame_num}`);
    }
}

main();