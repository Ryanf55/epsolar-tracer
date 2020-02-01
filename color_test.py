


class rgb_limiter():
    def __init__(self):
        self.max_v = 14
        self.min_v = 12

        self.max_r = 255
        self.min_r = 0
        self.max_g = 255
        self.min_g = 0


    def get_rgb(self,cur_v):
        v_scale = (cur_v - self.min_v) /  (self.max_v - self.min_v)
        r_val = round((1 - v_scale)* (self.max_r - self.min_r) + self.min_r)
        g_val = round((v_scale)* (self.max_g - self.min_g) + self.min_g)

        return r_val*65536 + g_val*256 + 0 

