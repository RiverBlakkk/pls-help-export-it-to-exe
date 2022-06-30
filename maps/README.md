# the .tiemap format

This is a binary format for storing a map, stored as a series of elements.

## .tiemap.txt

same as .tiemap but in hex

## metadata header

### empty byte

Eases automatic detection of file format

### position size

One byte, describing the size of the position data.
For example if two, each position coordinate is stored as a two byte integer.

## element list

Each element starts with a single byte describing the type of element.

The types describe:

- 0: [comment or editor specific metadata](#comment)
- 1: [tile](#tile)
- 2: [player spawn](#player-spawn)

### comment

Two bytes are used to describe the length of the comment.
They are then followed by the comment itself.

For hexadecimal notation, instead of the length, ???? may be used to indicate
that the comment ends with a newline.

### tile

One byte describing the tile type is followed by the position of the tile, represented as two numbers of the size specified in the metadata header (see [here](#position-size)).

### player spawn

NOTE: only one player spawn may exist in a map.

This element only contains the position of the player spawn, represented as two numbers of the size specified in the metadata header (see [here](#position-size)).
