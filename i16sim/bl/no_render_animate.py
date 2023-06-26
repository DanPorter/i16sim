import bpy

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"
    bl_options = {"REGISTER", "UNDO"}

    index : bpy.props.IntProperty(default=0)
    _timer = None
    _length = 0

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'} or self.index >= self._length:
            self.index = 0
            self.cancel(context)
            scan_once,steps,scan_cleanup=context.scene.animate_instructions
            scan_cleanup()
            print('Animation finished')
            print()
            return {'FINISHED'}

        if event.type == 'TIMER':
            try:
                scan_once,steps,scan_cleanup=context.scene.animate_instructions
                val=steps[self.index]
                scan_once(val)
                self.index += 1
            except:
                self.cancel(context)
                raise Exception("Animation failed. Please call via 'scan' function with 'animate' argument")

        return {'PASS_THROUGH'}

    def execute(self, context):
        try:
            wm = context.window_manager
            wait=context.scene.animate_wait
            self._length=len(context.scene.animate_instructions[1])
            self._timer = wm.event_timer_add(time_step=wait, window=context.window)
            wm.modal_handler_add(self)
        except:
            self.cancel(context)
            raise Exception('Could not start animation')
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.types.Scene.animate_wait=1
    bpy.types.Scene.animate_instructions=[None,[],None]
    bpy.utils.register_class(ModalTimerOperator)
    


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)
    del bpy.types.Scene.animate_wait
    del bpy.types.Scene.animate_instructions


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.wm.modal_timer_operator()