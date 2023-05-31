class Block():
    min = None
    max = None
    max_mv_amp = 0.0

    def __init__(self,x,y,w,h):
        self.coord   = (x,y,w,h)
        self.center  = (x+w//2,y+h//2)
        self.mv      = (0,0)
        self.mv_amp  = 0

    def check_inside_frame(self,x,y):
        """check if the searched box inside the target frame"""
        check = True
        if x<Block.min[0] or x>Block.max[0] \
            or y<Block.min[1] or y>Block.max[1]:
            check = False
        return check

    def calculate_mv_amp(self):
        """calculate L2 norm of motion-vector"""
        amp = (self.mv[0]**2 + self.mv[1]**2)**0.5
        #print(f"amp for block at {self.coord}: {amp}") 
        if amp > Block.max_mv_amp:
            Block.max_mv_amp = amp
        self.mv_amp = amp

    def __str__(self):
        return f"""
                Block: 
                coord={self.coord}, 
                center={self.center}, 
                mv={self.mv}, 
                mv_amp={self.mv_amp},
                min={Block.min},
                max={Block.max},
                max_mv_amp={Block.max_mv_amp}
        """
