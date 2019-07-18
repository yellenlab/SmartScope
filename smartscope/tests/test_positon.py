import unittest
import smartscope.source.position as pos

class TestPosition(unittest.TestCase):

    def setUp(self):
        self.stage  = pos.StagePosition(x=0)
        self.stage2 = pos.StagePosition(x=3, y=4, z=0)
        self.stage3 = pos.StagePosition(x=0, y=0, z=0)
        self.stage4 = pos.StagePosition(x=100, y=30, z=15)
        self.stage5 = pos.StagePosition(x=0, y=0, z=0)

        self.stagelist = [self.stage, self.stage2, self.stage3, self.stage4]
        self.stagelist2 = [self.stage2, self.stage]

        print (self.stage)
        print (self.stage2)
        print (self.stage3)
        print (self.stage4)

    def test_StagePosition(self):
        # Test __eq__() function 
        assert (self.stage==self.stage2) is False, 'StagePosition __eq__() error'
        assert (self.stage==self.stage3) is False, 'StagePosition __eq__() error'
        assert (self.stage3==self.stage5) is True, 'StagePosition __eq__() error'

        # Test dist()
        assert self.stage3.dist(self.stage5) == 0, 'StagePosition dist() error'
        assert self.stage2.dist(self.stage3) == 5, 'StagePosition dist() error'
        assert self.stage3.dist(self.stage4) == 105.475116, 'StagePosition dist() error'
        
    def test_PositionList(self):
        # Test __init__(), append()
        posit = pos.PositionList(stage)
        posit.append(stage2)
        posit2 = pos.PositionList(stage)
        posit2.append(stage2)
        posit3 = pos.PositionList(positions=stagelist)

        # Test __len__()
        assert len(posit3) == 4, 'PositionList __len__() error'
        assert len(posit) == 2, 'PositionList __len__() error'
        assert len(posit2) == 2, 'PositionList __len__() error'

        # Test __add__()
        p = posit + posit3
        p2 = posit + posit2
        assert len(p) == 6, 'PositionList __add__() error'
        assert len(p) == 4, 'PositionList __add__() error'

        # Test __iter__()
        ctr = 0
        for position in p:
            ctr += 1
        assert ctr == len(p), 'PositionList __iter__() error'

        # Test __getitem__(), __setitem__(), __delitem__()
        assert p[1].x == 3, 'PositionList __getitem__() error'
        assert p[4].z == 15, 'PositionList __getitem__() error'

        p[1].x = 4
        assert p[1].x == 4, 'PositionList __setitem__() error'
        
        prevlen = len(p)
        del p[1]
        assert len(p) == prevlen - 1, 'PositionList __delitem__() error'

        # Test save(), load()
        p.save('test', './')
        loaded = pos.load('test', './')

        same = True
        for  i, position in enumerate(loaded):
            if not position == p[i]:
                same = False
        assert same is True, 'PositionList save/load error'


if __name__ == '__main__':
    unittest.main()